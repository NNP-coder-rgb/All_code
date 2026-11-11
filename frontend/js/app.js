/**
 * app.js — HYBRID.STORE Global Application Coordinator
 * -------------------------------------------------------------
 * Chức năng:
 *  1. Đồng bộ số lượng giỏ hàng (Cart Badge) tự động trên toàn hệ thống và giữa các tab
 *  2. Phím tắt toàn cục:
 *     - `/` hoặc `Ctrl+K`: Focus nhanh vào thanh tìm kiếm
 *     - `Alt+T` hoặc `Ctrl+J`: Chuyển đổi giao diện Sáng / Tối (Theme Toggle)
 *     - `Escape`: Đóng nhanh các modal hoặc menu đang mở
 *  3. Quản lý trạng thái kết nối mạng (Online/Offline status notifications)
 *  4. Tự động hỗ trợ nút cuộn lên đầu trang (Back to top)
 *  5. Tương thích môi trường trình duyệt và Node.js test
 */

(function (root, factory) {
  if (typeof module === "object" && typeof module.exports === "object") {
    module.exports = factory();
  } else {
    root.HybridApp = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const STORAGE_KEYS = {
    THEME: "hv_theme",
    CART: "hv_cart",
  };

  /**
   * Cập nhật số lượng giỏ hàng hiển thị trên Header
   */
  function syncCartBadge() {
    if (typeof window === "undefined" || typeof localStorage === "undefined") return 0;
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.CART);
      let count = 0;
      if (raw) {
        const cart = JSON.parse(raw);
        if (Array.isArray(cart)) {
          count = cart.reduce((sum, item) => sum + (parseInt(item.quantity || item.qty, 10) || 1), 0);
        } else if (typeof cart === "object" && cart !== null) {
          const items = cart.items || cart.products || [];
          if (Array.isArray(items)) {
            count = items.reduce((sum, item) => sum + (parseInt(item.quantity || item.qty, 10) || 1), 0);
          }
        }
      }

      const badges = document.querySelectorAll(".cart-badge, [data-cart-badge], .badge-cart-count");
      badges.forEach((b) => {
        b.textContent = count > 99 ? "99+" : count;
        if (count > 0) {
          b.classList.remove("hidden", "d-none");
          b.style.display = "";
        } else {
          // Nếu cấu hình ẩn khi 0
          if (b.dataset.hideZero === "true") {
            b.style.display = "none";
          }
        }
      });
      return count;
    } catch (e) {
      console.warn("[app.js] Không thể đồng bộ giỏ hàng:", e);
      return 0;
    }
  }

  /**
   * Chuyển đổi Theme Sáng / Tối
   */
  function toggleTheme(forcedTheme) {
    if (typeof document === "undefined") return;
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const nextTheme = forcedTheme || (currentTheme === "dark" ? "light" : "dark");
    document.documentElement.setAttribute("data-theme", nextTheme);
    try {
      localStorage.setItem(STORAGE_KEYS.THEME, nextTheme);
    } catch (e) {}

    // Thông báo nếu có toast
    if (typeof window !== "undefined" && window.Utils && typeof window.Utils.toast === "function") {
      window.Utils.toast({
        title: "Giao diện",
        message: `Đã đổi sang giao diện ${nextTheme === "dark" ? "Tối (Cyber)" : "Sáng (Clean)"}`,
        type: "info",
        duration: 2000,
      });
    }
    return nextTheme;
  }

  /**
   * Khởi tạo Theme từ localStorage
   */
  function initTheme() {
    if (typeof document === "undefined" || typeof localStorage === "undefined") return;
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.THEME);
      if (saved) {
        document.documentElement.setAttribute("data-theme", saved);
      }
    } catch (e) {}
  }

  /**
   * Thiết lập phím tắt toàn cục
   */
  function setupKeyboardShortcuts() {
    if (typeof window === "undefined") return;

    window.addEventListener("keydown", function (e) {
      const activeEl = document.activeElement;
      const isInputActive =
        activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA" || activeEl.isContentEditable);

      // Phím tắt '/' hoặc Ctrl+K để focus tìm kiếm
      if ((e.key === "/" && !isInputActive) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k")) {
        e.preventDefault();
        const searchInput = document.querySelector(
          "#globalSearchInput, input[type='search'], .header-search input, input[name='q']"
        );
        if (searchInput) {
          searchInput.focus();
          if (searchInput.select) searchInput.select();
        }
      }

      // Phím tắt Alt+T hoặc Ctrl+J: Đổi theme
      if ((e.altKey && e.key.toLowerCase() === "t") || (e.ctrlKey && e.key.toLowerCase() === "j")) {
        e.preventDefault();
        toggleTheme();
      }

      // Phím Escape: Đóng modal / drawer
      if (e.key === "Escape") {
        const openModals = document.querySelectorAll(".modal.active, .modal.show, [data-modal].open");
        openModals.forEach((m) => {
          m.classList.remove("active", "show", "open");
        });
      }
    });
  }

  /**
   * Lắng nghe sự kiện đồng bộ storage giữa các tab
   */
  function setupStorageListener() {
    if (typeof window === "undefined") return;
    window.addEventListener("storage", function (e) {
      if (e.key === STORAGE_KEYS.CART) {
        syncCartBadge();
      } else if (e.key === STORAGE_KEYS.THEME && e.newValue) {
        document.documentElement.setAttribute("data-theme", e.newValue);
      }
    });
  }

  /**
   * Hỗ trợ nút cuộn lên đầu trang (Back to top)
   */
  function setupBackToTop() {
    if (typeof window === "undefined" || typeof document === "undefined") return;
    const bttBtn = document.querySelector("#backToTop, .btn-back-to-top, [data-back-to-top]");
    if (!bttBtn) return;

    window.addEventListener("scroll", function () {
      if (window.scrollY > 400) {
        bttBtn.classList.add("visible");
        bttBtn.style.opacity = "1";
        bttBtn.style.pointerEvents = "auto";
      } else {
        bttBtn.classList.remove("visible");
        bttBtn.style.opacity = "0";
        bttBtn.style.pointerEvents = "none";
      }
    });

    bttBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /**
   * Khởi động toàn bộ ứng dụng khi DOM đã sẵn sàng
   */
  function init() {
    if (typeof document === "undefined") return;
    initTheme();
    syncCartBadge();
    setupKeyboardShortcuts();
    setupStorageListener();
    setupBackToTop();
  }

  // Tự động chạy khi nạp trên trình duyệt
  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }

  return {
    init,
    syncCartBadge,
    toggleTheme,
    initTheme,
  };
});
