/**
 * catalog.js — Quản lý toàn bộ tính năng Lọc, Sắp xếp, Phân trang và Đếm ngược của Catalog
 * Sử dụng trực tiếp bộ hàm tiện ích utils.js trên dữ liệu PRODUCTS từ mock_data.js
 */

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Kiểm tra phụ thuộc bắt buộc
  if (typeof Utils === "undefined") {
    console.error("[catalog.js] Thiếu thư viện js/utils.js");
    return;
  }
  if (typeof PRODUCTS === "undefined") {
    console.error("[catalog.js] Thiếu dữ liệu PRODUCTS từ js/mock_data.js");
    return;
  }

  /* ---------------- TRẠNG THÁI CATALOG ---------------- */
  const urlParams = new URLSearchParams(window.location.search);
  const initialCategory = urlParams.get("cat") || "all";
  const initialKeyword = urlParams.get("q") || "";
  const initialType = urlParams.get("type") || "all";

  const state = {
    filters: {
      keyword: initialKeyword,
      category: initialCategory,
      type: initialType,
      minPrice: null,
      maxPrice: null,
      minRating: null,
      minCond: null,
    },
    sortKey: "default",
    page: 1,
    pageSize: 18, // Tăng thêm 10 sản phẩm mỗi trang (từ 8 lên 18 sản phẩm/trang)
  };

  /* ---------------- THAM CHIẾU DOM ---------------- */
  const dom = {
    grid: $("#catalogGrid"),
    countText: $("#catalogCountText"),
    activeFilters: $("#activeFilters"),
    paginationBar: $("#paginationBar"),
    sortSelect: $("#sortSelect"),
    pageSizeSelect: $("#pageSizeSelect"),
    resetBtn: $("#resetFilterBtn"),
    // Filter inputs
    keywordInput: $("#filterKeyword"),
    minPriceInput: $("#filterMinPrice"),
    maxPriceInput: $("#filterMaxPrice"),
    applyPriceBtn: $("#applyPriceBtn"),
    quickPriceBtns: $$(".price-tag"),
    categoryRadios: $$("input[name='filterCategory']"),
    typeRadios: $$("input[name='filterType']"),
    ratingRadios: $$("input[name='filterRating']"),
    condRadios: $$("input[name='filterCond']"),
    // Flash sale countdown
    sidebarCountdown: $("#sidebarCountdown"),
    // Header cart
    cartCount: $("#cartCount"),
    headerSearch: $("#headerSearchInput"),
    avatarBtn: $("#avatarBtn"),
  };

  /* ---------------- QUẢN LÝ TÀI KHOẢN & AVATAR ---------------- */
  function setupAvatar() {
    const avatarBtn = dom.avatarBtn;
    if (!avatarBtn) return;
    const user = typeof Auth !== "undefined" ? Auth.current() : null;
    if (user) {
      const initials = (user.fullName || "User")
        .trim()
        .split(/\s+/)
        .slice(-2)
        .map((w) => w[0])
        .join("")
        .toUpperCase();
      avatarBtn.textContent = initials;
      avatarBtn.title = user.fullName;
    }
    avatarBtn.addEventListener("click", () => {
      if (!user) {
        window.location.href = "../account/auth_login.html";
        return;
      }
      window.location.href = "../account/profile.html";
    });

    const btnHeaderPost = $("#btnHeaderPost");
    if (btnHeaderPost) {
      btnHeaderPost.addEventListener("click", (e) => {
        if (!Auth.current()) {
          e.preventDefault();
          Auth.ensureLogin(() => {
            window.location.href = "../seller/post_item.html";
          }, {
            title: "Đăng Bán Đồ Cũ",
            message: "Vui lòng đăng nhập tài khoản người bán để đăng tin bán đồ cũ.",
            returnUrl: "../seller/post_item.html"
          });
        }
      });
    }
  }

  /* ---------------- GIỎ HÀNG ---------------- */
  const CART_KEY = "hv_cart_count";
  function getCartCount() {
    try {
      return parseInt(localStorage.getItem(CART_KEY), 10) || 0;
    } catch (e) {
      return 0;
    }
  }
  function setCartCount(n) {
    try {
      localStorage.setItem(CART_KEY, n);
    } catch (e) {}
    if (dom.cartCount) {
      dom.cartCount.textContent = n;
      dom.cartCount.classList.toggle("hidden", n === 0);
    }
  }
  setCartCount(getCartCount());

  /* ---------------- TIỆN ÍCH TẠO THẺ SẢN PHẨM ---------------- */
  function createProductCardHTML(p) {
    const isMall = p.type === "mall";
    const title = p.short || p.name;
    const formattedPrice = Utils.formatCurrency(p.price);
    const formattedOldPrice = p.oldPrice ? Utils.formatCurrency(p.oldPrice) : "";
    const starsHtml = Utils.renderStars(p.rating || 4.5, { html: true });
    const starsText = Utils.renderStars(p.rating || 4.5);

    if (isMall) {
      return (
        '<article class="product-card" data-id="' +
        p.id +
        '">' +
        '<div class="product-media">' +
        '<a href="product_new.html?id=' + p.id + '">' +
        '<img src="' +
        p.img +
        '" alt="' +
        title +
        '" loading="lazy">' +
        '</a>' +
        '<div class="product-tags">' +
        '<span class="badge badge-solid">' +
        p.badge +
        "</span>" +
        (p.off ? '<span class="badge badge-success">-' + p.off + "%</span>" : "") +
        "</div>" +
        (p.tag ? '<span class="media-tag">' + p.tag + "</span>" : "") +
        "</div>" +
        '<div class="product-body">' +
        '<span class="product-cat text-primary">' +
        (p.sub || "CHÍNH HÃNG MALL") +
        "</span>" +
        '<h3 class="product-name line-clamp-2" title="' +
        p.name +
        '">' +
        '<a href="product_new.html?id=' + p.id + '" class="text-hover-primary">' +
        p.name +
        '</a>' +
        "</h3>" +
        '<div class="stars-container">' +
        starsHtml +
        '<span class="stars-text" title="' +
        starsText +
        '">(' +
        (p.rating ? p.rating.toFixed(1) : "5.0") +
        ")</span>" +
        "</div>" +
        '<div class="product-price mt-2">' +
        '<span class="price">' +
        formattedPrice +
        "</span>" +
        (formattedOldPrice ? '<span class="price-old">' + formattedOldPrice + "</span>" : "") +
        "</div>" +
        "</div>" +
        '<div class="product-actions">' +
        '<button class="btn btn-outlined btn-sm" type="button" data-action="add-cart" data-id="' +
        p.id +
        '"><span class="material-symbols-outlined icon-sm">shopping_cart</span> Thêm Giỏ</button>' +
        '<button class="btn btn-primary btn-sm" type="button" data-action="buy" data-id="' +
        p.id +
        '">Mua Ngay</button>' +
        "</div>" +
        "</article>"
      );
    }

    // Hàng C2C Đồ cũ / đã qua sử dụng
    const discount = p.oldPrice ? Math.round((1 - p.price / p.oldPrice) * 100) : 0;
    const savedAmount = p.oldPrice ? p.oldPrice - p.price : 0;
    const badgeCls = p.limited ? "badge badge-limited" : "badge badge-solid-secondary";
    return (
      '<article class="product-card" data-id="' +
      p.id +
      '">' +
      '<div class="product-media">' +
      '<a href="product_used.html?id=' + p.id + '">' +
      '<img src="' +
      p.img +
      '" alt="' +
      title +
      '" loading="lazy">' +
      '</a>' +
      '<div class="product-tags">' +
      '<span class="' +
      badgeCls +
      '">' +
      (p.badge || "ĐỒ CŨ LIKE NEW") +
      "</span>" +
      (discount > 0 ? '<span class="badge badge-success">Rẻ hơn đồ mới ' + discount + '%</span>' : '') +
      '<span class="badge badge-secondary">' +
      (p.condText || p.cond + "% Mới") +
      "</span>" +
      "</div>" +
      (p.tag ? '<span class="media-tag">' + p.tag + "</span>" : "") +
      "</div>" +
      '<div class="product-body">' +
      '<div class="cond">' +
      '<div class="progress-label"><span>' +
      (p.condPrefix || "Độ mới") +
      ": <strong>" +
      (p.condLabel || p.cond + "%") +
      "</strong></span>" +
      '<strong class="text-secondary">' +
      p.cond +
      "%</strong></div>" +
      '<div class="progress progress-secondary" style="--value:' +
      p.cond +
      '%"><div class="progress-bar"></div></div>' +
      "</div>" +
      '<div class="product-meta mt-1">' +
      '<span class="material-symbols-outlined icon-sm text-secondary">verified</span>' +
      '<span class="truncate">' +
      (p.seller || p.sellerName || "Người bán uy tín") +
      "</span>" +
      "</div>" +
      '<h3 class="product-name line-clamp-2" title="' +
      p.name +
      '">' +
      '<a href="product_used.html?id=' + p.id + '" class="text-hover-primary">' +
      p.name +
      '</a>' +
      "</h3>" +
      '<div class="product-price mt-2">' +
      '<span class="price">' +
      formattedPrice +
      "</span>" +
      (formattedOldPrice ? '<span class="price-old" title="Giá hàng mới 100%">Giá mới: ' + formattedOldPrice + '</span>' : '') +
      "</div>" +
      (discount > 0 ? '<div class="text-xs text-success fw-600 mt-1">Tiết kiệm ' + discount + '% (' + Utils.formatCurrency(savedAmount) + ') so với mua mới</div>' : '') +
      "</div>" +
      '<div class="product-actions c2c-actions">' +
      '<button class="btn btn-outlined btn-sm" type="button" data-action="add-cart" data-id="' +
      p.id +
      '" title="Thêm vào giỏ hàng"><span class="material-symbols-outlined icon-sm">shopping_cart</span> Thêm Giỏ</button>' +
      '<button class="btn btn-secondary btn-sm" type="button" data-action="offer" data-id="' +
      p.id +
      '"><span class="material-symbols-outlined icon-sm">handshake</span> Trả Giá</button>' +
      '<button class="btn btn-accent btn-sm btn-buy-now" type="button" data-action="buy" data-id="' +
      p.id +
      '">Mua Ngay</button>' +
      "</div>" +
      "</article>"
    );
  }

  /* ---------------- RENDER ACTIVE FILTER CHIPS ---------------- */
  function renderActiveFilterChips() {
    if (!dom.activeFilters) return;
    const chips = [];

    if (state.filters.keyword) {
      chips.push({
        label: 'Từ khóa: "' + state.filters.keyword + '"',
        clear: () => {
          state.filters.keyword = "";
          if (dom.keywordInput) dom.keywordInput.value = "";
          if (dom.headerSearch) dom.headerSearch.value = "";
          render();
        },
      });
    }

    if (state.filters.category && state.filters.category !== "all") {
      const catNames = {
        fashion: "Thời Trang",
        sneakers: "Sneakers",
        tech: "Đồ Điện Tử",
        appliances: "Gia Dụng",
        audio: "Âm Thanh",
        gaming: "Gaming Gear",
        watches: "Đồng Hồ",
        camera: "Máy Ảnh",
      };
      chips.push({
        label: "Ngành: " + (catNames[state.filters.category] || state.filters.category),
        clear: () => {
          state.filters.category = "all";
          syncFilterInputs();
          render();
        },
      });
    }

    if (state.filters.type && state.filters.type !== "all") {
      chips.push({
        label: "Loại: " + (state.filters.type === "mall" ? "Hàng Mới 100%" : "Đồ Cũ / Like New"),
        clear: () => {
          state.filters.type = "all";
          syncFilterInputs();
          render();
        },
      });
    }

    if (state.filters.minPrice != null || state.filters.maxPrice != null) {
      let priceLabel = "Giá: ";
      if (state.filters.minPrice && state.filters.maxPrice) {
        priceLabel += Utils.formatCurrency(state.filters.minPrice) + " - " + Utils.formatCurrency(state.filters.maxPrice);
      } else if (state.filters.minPrice) {
        priceLabel += "≥ " + Utils.formatCurrency(state.filters.minPrice);
      } else {
        priceLabel += "≤ " + Utils.formatCurrency(state.filters.maxPrice);
      }
      chips.push({
        label: priceLabel,
        clear: () => {
          state.filters.minPrice = null;
          state.filters.maxPrice = null;
          if (dom.minPriceInput) dom.minPriceInput.value = "";
          if (dom.maxPriceInput) dom.maxPriceInput.value = "";
          dom.quickPriceBtns.forEach((b) => b.classList.remove("active"));
          render();
        },
      });
    }

    if (state.filters.minRating != null) {
      chips.push({
        label: "Đánh giá ≥ " + state.filters.minRating + "★",
        clear: () => {
          state.filters.minRating = null;
          syncFilterInputs();
          render();
        },
      });
    }

    if (state.filters.minCond != null) {
      chips.push({
        label: "Độ mới ≥ " + state.filters.minCond + "%",
        clear: () => {
          state.filters.minCond = null;
          syncFilterInputs();
          render();
        },
      });
    }

    dom.activeFilters.innerHTML = chips
      .map(
        (c, idx) =>
          '<span class="active-filter-chip">' +
          c.label +
          '<button type="button" data-chip-idx="' +
          idx +
          '" title="Xóa điều kiện">&times;</button>' +
          "</span>"
      )
      .join("");

    $$("button[data-chip-idx]", dom.activeFilters).forEach((btn) => {
      const idx = Number(btn.dataset.chipIdx);
      btn.addEventListener("click", () => chips[idx].clear());
    });
  }

  /* ---------------- RENDER THANH PHÂN TRANG ---------------- */
  function renderPagination(paginated) {
    if (!dom.paginationBar) return;

    if (paginated.total === 0) {
      dom.paginationBar.innerHTML = "";
      return;
    }

    const { page, totalPages, total, size, items } = paginated;
    const startItem = (page - 1) * size + 1;
    const endItem = startItem + items.length - 1;

    let buttonsHtml = "";

    // Nút Trước
    buttonsHtml +=
      '<button type="button" class="page-btn" data-page="' +
      (page - 1) +
      '"' +
      (page <= 1 ? " disabled" : "") +
      '><span class="material-symbols-outlined icon-sm">chevron_left</span></button>';

    // Các nút số trang
    for (let p = 1; p <= totalPages; p++) {
      if (
        p === 1 ||
        p === totalPages ||
        (p >= page - 1 && p <= page + 1)
      ) {
        buttonsHtml +=
          '<button type="button" class="page-btn' +
          (p === page ? " active" : "") +
          '" data-page="' +
          p +
          '">' +
          p +
          "</button>";
      } else if (
        (p === page - 2 && page > 3) ||
        (p === page + 2 && page < totalPages - 2)
      ) {
        buttonsHtml += '<span class="page-btn" style="border:none;background:none;pointer-events:none;">...</span>';
      }
    }

    // Nút Sau
    buttonsHtml +=
      '<button type="button" class="page-btn" data-page="' +
      (page + 1) +
      '"' +
      (page >= totalPages ? " disabled" : "") +
      '><span class="material-symbols-outlined icon-sm">chevron_right</span></button>';

    dom.paginationBar.innerHTML =
      '<div class="pagination-info">' +
      "Hiển thị <strong>" +
      startItem +
      " - " +
      endItem +
      "</strong> trong <strong>" +
      total +
      "</strong> sản phẩm" +
      "</div>" +
      '<div class="pagination">' +
      buttonsHtml +
      "</div>";

    // Gắn sự kiện click đổi trang
    $$("button[data-page]", dom.paginationBar).forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetPage = Number(btn.dataset.page);
        if (targetPage >= 1 && targetPage <= totalPages && targetPage !== page) {
          state.page = targetPage;
          render();
          const targetEl = $("#catalogMainTop");
          if (targetEl) targetEl.scrollIntoView({ behavior: "smooth" });
        }
      });
    });
  }

  /* ---------------- HÀM RENDER CHÍNH (LỌC, SẮP XẾP, PHÂN TRANG) ---------------- */
  function render() {
    // BƯỚC 1: LỌC ĐA ĐIỀU KIỆN bằng filterProducts
    const filtered = Utils.filterProducts(PRODUCTS, state.filters);

    // BƯỚC 2: SẮP XẾP bằng sortProducts
    const sorted = Utils.sortProducts(filtered, state.sortKey);

    // BƯỚC 3: PHÂN TRANG bằng paginate
    const paginated = Utils.paginate(sorted, state.page, state.pageSize);
    state.page = paginated.page; // đồng bộ lại nếu page bị clamp

    // BƯỚC 4: RENDER DANH SÁCH SẢN PHẨM
    if (dom.grid) {
      if (paginated.items.length === 0) {
        dom.grid.innerHTML =
          '<div class="empty-state">' +
          '<div class="empty-state-icon"><span class="material-symbols-outlined">inventory_2</span></div>' +
          '<h3 class="empty-state-title">Không tìm thấy sản phẩm nào</h3>' +
          '<p class="empty-state-desc">Hãy thử thay đổi khoảng giá, xóa từ khóa tìm kiếm hoặc chọn danh mục khác.</p>' +
          '<button type="button" class="btn btn-primary btn-sm mt-3" id="emptyResetBtn">' +
          '<span class="material-symbols-outlined icon-sm">restart_alt</span> Xóa Toàn Bộ Bộ Lọc' +
          "</button>" +
          "</div>";
        const emptyBtn = $("#emptyResetBtn");
        if (emptyBtn) emptyBtn.addEventListener("click", resetAllFilters);
      } else {
        dom.grid.innerHTML = paginated.items.map(createProductCardHTML).join("");
      }
    }

    // BƯỚC 5: CẬP NHẬT SỐ LƯỢNG KẾT QUẢ
    if (dom.countText) {
      dom.countText.innerHTML =
        "Tìm thấy <strong>" +
        paginated.total +
        "</strong> sản phẩm" +
        (paginated.totalPages > 1
          ? " (Trang " + paginated.page + "/" + paginated.totalPages + ")"
          : "");
    }

    // BƯỚC 6: RENDER CHIPS VÀ THANH PHÂN TRANG
    renderActiveFilterChips();
    renderPagination(paginated);
  }

  /* ---------------- ĐỒNG BỘ INPUT VỚI STATE ---------------- */
  function syncFilterInputs() {
    if (dom.keywordInput) dom.keywordInput.value = state.filters.keyword || "";
    if (dom.headerSearch) dom.headerSearch.value = state.filters.keyword || "";

    dom.categoryRadios.forEach((r) => {
      r.checked = r.value === state.filters.category;
    });

    dom.typeRadios.forEach((r) => {
      r.checked = r.value === state.filters.type;
    });

    dom.ratingRadios.forEach((r) => {
      if (state.filters.minRating == null) {
        r.checked = r.value === "all";
      } else {
        r.checked = String(r.value) === String(state.filters.minRating);
      }
    });

    dom.condRadios.forEach((r) => {
      if (state.filters.minCond == null) {
        r.checked = r.value === "all";
      } else {
        r.checked = String(r.value) === String(state.filters.minCond);
      }
    });

    if (dom.minPriceInput)
      dom.minPriceInput.value = state.filters.minPrice != null ? state.filters.minPrice : "";
    if (dom.maxPriceInput)
      dom.maxPriceInput.value = state.filters.maxPrice != null ? state.filters.maxPrice : "";
  }

  function resetAllFilters() {
    state.filters = {
      keyword: "",
      category: "all",
      type: "all",
      minPrice: null,
      maxPrice: null,
      minRating: null,
      minCond: null,
    };
    state.page = 1;
    dom.quickPriceBtns.forEach((b) => b.classList.remove("active"));
    syncFilterInputs();
    render();
    Utils.toast("Đã đặt lại toàn bộ bộ lọc về mặc định", "info");
  }

  /* ---------------- GẮN CÁC SỰ KIỆN LỌC & SẮP XẾP ---------------- */
  function setupFilterEvents() {
    // 1. Tìm kiếm theo từ khóa
    let searchDebounce = null;
    function handleSearch(val) {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        state.filters.keyword = val.trim();
        state.page = 1;
        render();
      }, 250);
    }

    if (dom.keywordInput) {
      dom.keywordInput.addEventListener("input", (e) => handleSearch(e.target.value));
    }
    if (dom.headerSearch) {
      dom.headerSearch.addEventListener("input", (e) => {
        if (dom.keywordInput) dom.keywordInput.value = e.target.value;
        handleSearch(e.target.value);
      });
    }

    // 2. Ngành hàng (Category)
    dom.categoryRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        if (e.target.checked) {
          state.filters.category = e.target.value;
          state.page = 1;
          render();
        }
      });
    });

    // 3. Loại hàng (Type: Mall / C2C)
    dom.typeRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        if (e.target.checked) {
          state.filters.type = e.target.value;
          state.page = 1;
          render();
        }
      });
    });

    // 4. Khoảng giá nhập tay
    if (dom.applyPriceBtn) {
      dom.applyPriceBtn.addEventListener("click", () => {
        const min = dom.minPriceInput.value ? Number(dom.minPriceInput.value) : null;
        const max = dom.maxPriceInput.value ? Number(dom.maxPriceInput.value) : null;
        if (min != null && max != null && min > max) {
          Utils.toast("Giá tối thiểu không được lớn hơn giá tối đa", "warning");
          return;
        }
        state.filters.minPrice = min;
        state.filters.maxPrice = max;
        state.page = 1;
        dom.quickPriceBtns.forEach((b) => b.classList.remove("active"));
        render();
      });
    }

    // 5. Nút giá nhanh (Dưới 5tr, 5-15tr, Trên 15tr)
    dom.quickPriceBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const isActive = btn.classList.contains("active");
        dom.quickPriceBtns.forEach((b) => b.classList.remove("active"));

        if (isActive) {
          state.filters.minPrice = null;
          state.filters.maxPrice = null;
          if (dom.minPriceInput) dom.minPriceInput.value = "";
          if (dom.maxPriceInput) dom.maxPriceInput.value = "";
        } else {
          btn.classList.add("active");
          const min = btn.dataset.min ? Number(btn.dataset.min) : null;
          const max = btn.dataset.max ? Number(btn.dataset.max) : null;
          state.filters.minPrice = min;
          state.filters.maxPrice = max;
          if (dom.minPriceInput) dom.minPriceInput.value = min != null ? min : "";
          if (dom.maxPriceInput) dom.maxPriceInput.value = max != null ? max : "";
        }
        state.page = 1;
        render();
      });
    });

    // 6. Đánh giá (Rating)
    dom.ratingRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        if (e.target.checked) {
          state.filters.minRating = e.target.value === "all" ? null : Number(e.target.value);
          state.page = 1;
          render();
        }
      });
    });

    // 7. Độ mới (Condition C2C)
    dom.condRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        if (e.target.checked) {
          state.filters.minCond = e.target.value === "all" ? null : Number(e.target.value);
          state.page = 1;
          render();
        }
      });
    });

    // 8. Đặt lại bộ lọc
    if (dom.resetBtn) {
      dom.resetBtn.addEventListener("click", resetAllFilters);
    }

    // 9. Sắp xếp (Sort)
    if (dom.sortSelect) {
      dom.sortSelect.addEventListener("change", (e) => {
        state.sortKey = e.target.value;
        state.page = 1;
        render();
      });
    }

    // 10. Số lượng hiển thị mỗi trang (Page Size)
    if (dom.pageSizeSelect) {
      dom.pageSizeSelect.addEventListener("change", (e) => {
        state.pageSize = Number(e.target.value) || 18;
        state.page = 1;
        render();
      });
    }
  }

  /* ---------------- XỬ LÝ CLICK SỰ KIỆN TRÊN CARD ---------------- */
  let currentOfferProduct = null;
  function setupProductCardEvents() {
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-action]");
      if (!btn) return;

      const action = btn.dataset.action;
      const id = btn.dataset.id;
      const product = PRODUCTS.find((p) => p.id === id);
      if (!product) return;

      const title = product.short || product.name;

      if (action === "add-cart") {
        if (!Auth.ensureLogin((user) => {
          Utils.Cart.addItem(product, 1);
        }, {
          title: "Đăng Nhập Mua Hàng",
          message: 'Vui lòng đăng nhập tài khoản để thêm "' + title + '" vào giỏ hàng.',
        })) {
          return;
        }
      } else if (action === "buy") {
        if (!Auth.ensureLogin((user) => {
          Utils.Cart.addItem(product, 1);
          window.location.href = "cart.html";
        }, {
          title: "Đăng Nhập Mua Hàng",
          message: 'Vui lòng đăng nhập tài khoản để mua ngay "' + title + '".',
          returnUrl: "cart.html"
        })) {
          return;
        }
      } else if (action === "offer") {
        if (!Auth.ensureLogin((user) => {
          currentOfferProduct = product;
          const pTitle = $("#offerProduct");
          const pSeller = $("#offerSeller");
          const pCond = $("#offerCond");
          const pPrice = $("#offerCurrent");
          const pInput = $("#offerPrice");

          if (pTitle) pTitle.textContent = title;
          if (pSeller) pSeller.textContent = product.sellerName || product.seller || "-";
          if (pCond) pCond.textContent = (product.cond || 99) + "%";
          if (pPrice) pPrice.textContent = Utils.formatCurrency(product.price);
          if (pInput)
            pInput.value = Math.round(product.price * 0.95).toLocaleString("vi-VN");

          Utils.openModal("offerModal");
        }, {
          title: "Yêu Cầu Đăng Nhập",
          message: 'Vui lòng đăng nhập tài khoản để gửi đề nghị trả giá cho "' + title + '".',
        })) {
          return;
        }
      }
    });

    // Form trả giá
    const offerForm = $("#offerForm");
    if (offerForm) {
      offerForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const priceInput = $("#offerPrice");
        const value = parseInt(String(priceInput.value || "").replace(/\D/g, ""), 10) || 0;
        if (value <= 0) {
          Utils.toast("Vui lòng nhập mức giá đề xuất hợp lệ!", "error");
          return;
        }

        Utils.closeModal("offerModal");
        Utils.toast(
          'Đã gửi đề xuất trả giá ' +
            Utils.formatCurrency(value) +
            ' cho "' +
            (currentOfferProduct ? currentOfferProduct.short || currentOfferProduct.name : "sản phẩm") +
            '"!',
          "success"
        );
      });
    }

    // Modal close buttons
    $$("[data-close]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const backdrop = btn.closest(".modal-backdrop");
        if (backdrop) Utils.closeModal(backdrop);
      });
    });

    // Click backdrop to close
    $$(".modal-backdrop").forEach((backdrop) => {
      backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) Utils.closeModal(backdrop);
      });
    });

    // Quick discount buttons in offer modal
    $$("[data-quick]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (!currentOfferProduct) return;
        const percent = Number(btn.dataset.quick);
        const newPrice = Math.round(currentOfferProduct.price * (1 + percent / 100));
        const input = $("#offerPrice");
        if (input) input.value = newPrice.toLocaleString("vi-VN");
      });
    });
  }

  /* ---------------- KHỞI TẠO ĐẾM NGƯỢC FLASH SALE 48 GIỜ ---------------- */
  function setupCountdown() {
    if (!dom.sidebarCountdown) return;
    // Đếm ngược 48 giờ ưu đãi flash sale
    const countdown48h = 48 * 3600;
    Utils.startCountdown(countdown48h, dom.sidebarCountdown, () => {
      dom.sidebarCountdown.innerHTML =
        '<span class="badge badge-success">Đợt ưu đãi mới đã bắt đầu</span>';
    });
  }

  /* ---------------- CUỘN NGANG KÉO THẢ CHO SUBNAV ---------------- */
  function enableHorizontalDrag(el) {
    if (!el) return;
    el.addEventListener("wheel", (e) => {
      if (e.deltaY !== 0 && el.scrollWidth > el.clientWidth) {
        e.preventDefault();
        el.scrollLeft += e.deltaY;
      }
    }, { passive: false });

    let isDown = false;
    let startX = 0;
    let scrollLeft = 0;
    let hasDragged = false;

    el.addEventListener("mousedown", (e) => {
      isDown = true;
      hasDragged = false;
      startX = e.pageX - el.offsetLeft;
      scrollLeft = el.scrollLeft;
      el.style.cursor = "grabbing";
    });

    window.addEventListener("mouseup", () => {
      isDown = false;
      if (el) el.style.cursor = "default";
    });

    el.addEventListener("mousemove", (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - el.offsetLeft;
      const walk = (x - startX) * 1.5;
      if (Math.abs(walk) > 5) hasDragged = true;
      el.scrollLeft = scrollLeft - walk;
    });

    el.addEventListener("click", (e) => {
      if (hasDragged) {
        e.preventDefault();
        e.stopPropagation();
      }
    }, true);
  }

  /* ---------------- KHỞI CHẠY ---------------- */
  setupAvatar();
  syncFilterInputs();
  setupFilterEvents();
  setupProductCardEvents();
  setupCountdown();
  render();
  enableHorizontalDrag($(".subnav .container"));
  if (typeof Utils !== "undefined" && Utils.Cart) {
    Utils.Cart.syncBadge();
  }
})();
