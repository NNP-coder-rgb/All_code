// index.js — trang chủ: dựng giao diện từ mock-data.js, giỏ hàng, trả giá, đăng bán, đăng xuất
// Cần nạp trước: popup.js, auth.js, mock-data.js
(function () {
  const $ = (sel, root) => (root || document).querySelector(sel);

  /* ---------------- Báo lỗi ngay trên trang (để không bị "trắng" mà không biết vì sao) ---------------- */
  function showFatal(lines) {
    console.error("[index.js]", lines.join(" | "));
    const box = document.createElement("div");
    box.className = "container section";
    box.innerHTML =
      '<div class="alert alert-danger"><span class="material-symbols-outlined alert-icon">error</span><div>' +
      '<div class="alert-title">Trang chủ chưa tải được dữ liệu</div>' +
      lines.map((l) => "<p>" + l + "</p>").join("") +
      "<p>Mở F12 → tab Console để xem lỗi chi tiết.</p></div></div>";
    const main = document.querySelector("main");
    main.insertBefore(box, main.firstChild);
  }

  // Kiểm tra các file cần thiết đã được nạp chưa
  const missing = [];
  if (typeof showPopup === "undefined")
    missing.push("Thiếu <code>js/popup.js</code> (hàm showPopup).");
  if (typeof Auth === "undefined")
    missing.push("Thiếu <code>js/auth.js</code> (đối tượng Auth).");
  if (typeof Utils === "undefined")
    missing.push("Thiếu <code>js/utils.js</code> (bộ hàm tiện ích Utils).");
  if (typeof PRODUCTS === "undefined")
    missing.push(
      "Thiếu biến <code>PRODUCTS</code> — kiểm tra <code>js/mock-data.js</code> có đúng file/đường dẫn và đúng tên biến không.",
    );
  if (typeof CATEGORIES === "undefined")
    missing.push(
      "Thiếu biến <code>CATEGORIES</code> trong <code>js/mock-data.js</code>.",
    );
  if (typeof FLASH_SALE === "undefined")
    missing.push(
      "Thiếu biến <code>FLASH_SALE</code> trong <code>js/mock-data.js</code>.",
    );
  if (typeof TICKER === "undefined")
    missing.push(
      "Thiếu biến <code>TICKER</code> trong <code>js/mock-data.js</code>.",
    );
  if (missing.length) {
    showFatal(missing);
    return;
  }

  // Lỗi JavaScript bất ngờ trong quá trình dựng trang cũng hiện ra trên màn hình
  window.addEventListener("error", (e) => {
    showFatal([
      "Lỗi JavaScript: <code>" +
        e.message +
        "</code> (" +
        String(e.filename || "")
          .split("/")
          .pop() +
        ":" +
        e.lineno +
        ")",
    ]);
  });

  // Muốn chỉ cho người đã đăng nhập xem trang chủ thì bỏ dấu // ở dòng dưới:
  // if (!Auth.requireLogin()) return;

  const fmt = (n) => (typeof formatCurrency === "function" ? formatCurrency(n) : n.toLocaleString("vi-VN") + "₫");
  const findProduct = (id) => PRODUCTS.find((p) => p.id === id);

  /* ---------------- Tài khoản ---------------- */
  const user = typeof Auth !== "undefined" && typeof Auth.current === "function" ? Auth.current() : null;
  const avatarBtn = $("#avatarBtn");
  if (user) {
    const initials = user.fullName
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
      window.location.href = "pages/account/auth_login.html";
      return;
    }
    window.location.href = "pages/account/profile.html";
  });

  /* ---------------- Tìm kiếm tương tác trang chủ ---------------- */
  const searchInput = $("#homeSearchInput");
  const searchForm = $("#homeSearchForm");
  const searchDropdown = $("#searchDropdown");

  if (searchInput && searchDropdown) {
    let searchDebounce = null;

    function renderSearchDropdown(keyword) {
      const q = (keyword || "").trim();
      if (!q) {
        searchDropdown.style.display = "none";
        searchDropdown.innerHTML = "";
        return;
      }

      // Lọc sản phẩm khớp từ khóa
      const matches = typeof Utils !== "undefined" && typeof Utils.filterProducts === "function"
        ? Utils.filterProducts(PRODUCTS, { keyword: q })
        : PRODUCTS.filter((p) => {
            const str = (p.name + " " + (p.short || "") + " " + (p.desc || "")).toLowerCase();
            return str.includes(q.toLowerCase());
          });

      const safeQ = typeof escapeHtml === "function" ? escapeHtml(q) : q.replace(/</g, "&lt;");

      if (matches.length === 0) {
        searchDropdown.innerHTML =
          '<div class="search-dropdown-empty">' +
          '<span class="material-symbols-outlined icon-md text-muted mb-1" style="display:block;font-size:28px;">search_off</span>' +
          '<div>Không tìm thấy sản phẩm khớp với "<strong>' + safeQ + '</strong>"</div>' +
          '<div class="text-xs text-muted mt-1">Gợi ý thử: iPhone, Nike, Sony, Dyson, MacBook, Jordan...</div>' +
          '</div>';
        searchDropdown.style.display = "block";
        return;
      }

      const topMatches = matches.slice(0, 6);
      let html = topMatches.map((p) => {
        const targetUrl = p.type === "mall"
          ? "pages/shop/product_new.html?id=" + p.id
          : "pages/shop/product_used.html?id=" + p.id;
        const badgeText = p.type === "mall" ? (p.badge || "MALL 100%") : (p.condText || "LIKE NEW");
        const categoryName = p.category === "fashion" ? "Thời Trang"
          : p.category === "sneakers" ? "Sneakers"
          : p.category === "tech" ? "Điện Tử"
          : "Gia Dụng";

        return (
          '<a class="search-dropdown-item" href="' + targetUrl + '">' +
          '<img src="' + p.img + '" alt="' + (p.short || p.name) + '">' +
          '<div class="item-info">' +
          '<div class="item-title">' + (p.short || p.name) + '</div>' +
          '<div class="item-sub">' +
          '<span class="badge badge-sm ' + (p.type === "mall" ? "badge-primary" : "badge-secondary") + '">' + badgeText + '</span>' +
          '<span>' + categoryName + '</span>' +
          '</div>' +
          '</div>' +
          '<div class="item-price">' + fmt(p.price) + '</div>' +
          '</a>'
        );
      }).join("");

      html +=
        '<a class="search-dropdown-footer" href="pages/shop/catalog.html?q=' + encodeURIComponent(q) + '">' +
        'Xem tất cả ' + matches.length + ' kết quả cho "' + safeQ + '" trong Bộ Sưu Tập →' +
        '</a>';

      searchDropdown.innerHTML = html;
      searchDropdown.style.display = "block";
    }

    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        renderSearchDropdown(e.target.value);
      }, 150);
    });

    searchInput.addEventListener("focus", (e) => {
      if (e.target.value.trim()) {
        renderSearchDropdown(e.target.value);
      }
    });

    // Bấm ESC hoặc click ra ngoài thì ẩn
    document.addEventListener("click", (e) => {
      if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.style.display = "none";
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        searchDropdown.style.display = "none";
      }
    });

    if (searchForm) {
      searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const q = searchInput.value.trim();
        if (q) {
          window.location.href = "pages/shop/catalog.html?q=" + encodeURIComponent(q);
        } else {
          window.location.href = "pages/shop/catalog.html";
        }
      });
    }
  }

  /* ---------------- Dòng chạy Giao Dịch Mới ---------------- */
  const tickerHTML = TICKER.map(
    (t) =>
      '<span class="ticker-item tone-' +
      t.tone +
      '"><i></i><strong>' +
      t.id +
      "</strong> " +
      t.html +
      "</span>",
  ).join("");
  $("#tickerInner").innerHTML = tickerHTML + tickerHTML; // nhân đôi để chạy vòng liền mạch

  /* ---------------- Chip ngành hàng + ô chỉ mục ---------------- */
  $("#chipBar").innerHTML =
    '<a class="chip active" href="pages/shop/catalog.html"><span class="material-symbols-outlined">grid_view</span>Tất Cả Ngành Hàng</a>' +
    CATEGORIES.map(
      (c) =>
        '<a class="chip tone-' +
        c.tone +
        '" href="#cat-' +
        c.id +
        '">' +
        '<span class="material-symbols-outlined" style="color:var(--tone)">' +
        c.chipIcon +
        "</span>" +
        c.chip +
        '<span class="chip-count">' +
        c.total +
        "</span>" +
        "</a>",
    ).join("");

  // Bắt sự kiện chuyển active và cuộn mượt cho các chip ngành hàng
  const chipEls = $$("#chipBar .chip");
  chipEls.forEach((chip) => {
    chip.addEventListener("click", (e) => {
      chipEls.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      const targetId = chip.getAttribute("href");
      if (targetId && targetId.startsWith("#cat-")) {
        const targetEl = $(targetId);
        if (targetEl) {
          e.preventDefault();
          targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });

  // Hỗ trợ cuộn ngang tự nhiên bằng con lăn chuột (mouse wheel) và kéo chuột (drag)
  const chipBar = $("#chipBar");
  if (chipBar) {
    chipBar.addEventListener("wheel", (e) => {
      if (e.deltaY !== 0 && chipBar.scrollWidth > chipBar.clientWidth) {
        e.preventDefault();
        chipBar.scrollLeft += e.deltaY;
      }
    }, { passive: false });

    let isDown = false;
    let startX = 0;
    let scrollLeft = 0;
    let hasDragged = false;

    chipBar.addEventListener("mousedown", (e) => {
      isDown = true;
      hasDragged = false;
      startX = e.pageX - chipBar.offsetLeft;
      scrollLeft = chipBar.scrollLeft;
      chipBar.style.cursor = "grabbing";
    });

    window.addEventListener("mouseup", () => {
      isDown = false;
      if (chipBar) chipBar.style.cursor = "default";
    });

    chipBar.addEventListener("mousemove", (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - chipBar.offsetLeft;
      const walk = (x - startX) * 1.5;
      if (Math.abs(walk) > 5) hasDragged = true;
      chipBar.scrollLeft = scrollLeft - walk;
    });

    chipBar.addEventListener("click", (e) => {
      if (hasDragged) {
        e.preventDefault();
        e.stopPropagation();
      }
    }, true);
  }

  $("#catJump").innerHTML = CATEGORIES.map(
    (c) =>
      '<a class="cat-jump tone-' +
      c.tone +
      '" href="#cat-' +
      c.id +
      '">' +
      '<span class="material-symbols-outlined">' +
      c.icon +
      "</span>" +
      "<div><strong>" +
      c.tile +
      "</strong><small>" +
      c.tileCount +
      "</small></div></a>",
  ).join("");

  /* ---------------- Thẻ sản phẩm ---------------- */
  function cardHTML(p, ctx) {
    const flash = ctx === "flash";
    const title = p.short || p.name;

    if (p.type === "mall") {
      return (
        '<article class="product-card">' +
        '<div class="product-media">' +
        '<a href="pages/shop/product_new.html?id=' + p.id + '">' +
        '<img src="' +
        p.img +
        '" alt="' +
        title +
        '" loading="lazy">' +
        '</a>' +
        '<div class="product-tags"><span class="badge badge-solid">' +
        p.badge +
        "</span>" +
        (flash ? '<span class="badge">-' + p.off + "%</span>" : "") +
        "</div>" +
        (p.tag && !flash
          ? '<span class="media-tag">' + p.tag + "</span>"
          : "") +
        "</div>" +
        '<div class="product-body">' +
        '<span class="product-cat text-primary">' +
        p.sub +
        "</span>" +
        '<h3 class="product-name line-clamp-2">' +
        '<a href="pages/shop/product_new.html?id=' + p.id + '" class="text-hover-primary">' +
        p.name +
        '</a>' +
        "</h3>" +
        (p.rating
          ? '<div class="product-meta"><span class="stars" title="' + (typeof renderStars === "function" ? renderStars(p.rating) : "") + '">★ ' +
            p.rating.toFixed(1) +
            "</span><span>" +
            p.reviews +
            "</span></div>"
          : "") +
        '<div class="product-price"><span class="price" style="color:var(--primary-200)">' +
        fmt(p.price) +
        "</span>" +
        (flash && p.oldPrice
          ? '<span class="price-old">' + fmt(p.oldPrice) + "</span>"
          : '<span class="badge badge-success">-' + p.off + "%</span>") +
        "</div>" +
        "</div>" +
        '<div class="product-actions single">' +
        (flash
          ? '<button class="btn btn-primary btn-sm" data-action="add-cart" data-id="' +
            p.id +
            '"><span class="material-symbols-outlined icon-sm">shopping_cart</span>Thêm Giỏ Hàng</button>'
          : '<button class="btn btn-outlined btn-sm" data-action="buy" data-id="' +
            p.id +
            '">' +
            (p.buy || "Mua Ngay") +
            "</button>") +
        "</div>" +
        "</article>"
      );
    }

    // c2c — đồ cũ / đã qua sử dụng
    const discount = p.oldPrice ? Math.round((1 - p.price / p.oldPrice) * 100) : 0;
    const badgeCls = p.limited
      ? "badge badge-limited"
      : "badge badge-solid-secondary";
    return (
      '<article class="product-card">' +
      '<div class="product-media">' +
      '<a href="pages/shop/product_used.html?id=' + p.id + '">' +
      '<img src="' +
      p.img +
      '" alt="' +
      title +
      '" loading="lazy">' +
      '</a>' +
      '<div class="product-tags"><span class="' +
      badgeCls +
      '">' +
      (p.badge || "ĐỒ CŨ LIKE NEW") +
      "</span>" +
      (discount > 0 ? '<span class="badge badge-success">Rẻ hơn đồ mới ' + discount + '%</span>' : '') +
      '<span class="badge badge-secondary">' +
      p.condText +
      "</span></div>" +
      (p.tag ? '<span class="media-tag">' + p.tag + "</span>" : "") +
      "</div>" +
      '<div class="product-body">' +
      '<div class="cond">' +
      '<div class="progress-label"><span>' +
      p.condPrefix +
      ": <strong>" +
      p.condLabel +
      "</strong></span>" +
      '<strong class="text-secondary">' +
      p.cond +
      "%</strong></div>" +
      '<div class="progress progress-secondary" style="--value:' +
      p.cond +
      '%"><div class="progress-bar"></div></div>' +
      "</div>" +
      '<div class="product-meta"><span class="material-symbols-outlined icon-sm">verified</span>' +
      p.seller +
      "</div>" +
      '<h3 class="product-name line-clamp-2">' +
      '<a href="pages/shop/product_used.html?id=' + p.id + '" class="text-hover-primary">' +
      p.name +
      '</a>' +
      "</h3>" +
      (p.desc
        ? '<p class="text-xs text-muted truncate">' + p.desc + "</p>"
        : "") +
      '<div class="product-price"><span class="price">' +
      fmt(p.price) +
      "</span>" +
      (p.oldPrice ? '<span class="price-old" title="Giá hàng mới 100%">Giá mới: ' + fmt(p.oldPrice) + '</span>' : '') +
      "</div>" +
      (discount > 0 ? '<div class="text-xs text-success fw-600 mt-1">Tiết kiệm ' + discount + '% (' + fmt(p.oldPrice - p.price) + ') so với mua mới</div>' : '') +
      "</div>" +
      '<div class="product-actions">' +
      '<button class="btn btn-secondary btn-sm" data-action="offer" data-id="' +
      p.id +
      '">Trả Giá</button>' +
      '<button class="btn btn-accent btn-sm" data-action="buy" data-id="' +
      p.id +
      '">Mua Ngay</button>' +
      "</div>" +
      "</article>"
    );
  }

  /* ---------------- Flash sale ---------------- */
  $("#flashGrid").innerHTML = FLASH_SALE.items
    .map((id) => cardHTML(findProduct(id), "flash"))
    .join("");

  const countdownEls = { h: $("#fs-h"), m: $("#fs-m"), s: $("#fs-s") };
  if (typeof startCountdown === "function") {
    startCountdown(FLASH_SALE.endsInSeconds, countdownEls, () => {
      startCountdown(4 * 3600, countdownEls);
    });
  } else {
    let seconds = FLASH_SALE.endsInSeconds;
    const pad = (n) => String(n).padStart(2, "0");
    setInterval(() => {
      seconds = seconds <= 0 ? 4 * 3600 : seconds - 1;
      countdownEls.h.textContent = pad(Math.floor(seconds / 3600));
      countdownEls.m.textContent = pad(Math.floor((seconds % 3600) / 60));
      countdownEls.s.textContent = pad(seconds % 60);
    }, 1000);
  }

  /* ---------------- Các khối ngành hàng ---------------- */
  $("#categorySections").innerHTML = CATEGORIES.map((c) => {
    const items = PRODUCTS.filter((p) => p.category === c.id && !p.flashOnly);
    if (!items || items.length === 0) return "";
    return (
      '<section class="container section tone-' +
      c.tone +
      '" id="cat-' +
      c.id +
      '">' +
      '<div class="cat-head">' +
      '<div class="cat-title">' +
      '<span class="icon-box"><span class="material-symbols-outlined icon-lg">' +
      c.icon +
      "</span></span>" +
      "<div>" +
      '<div class="flex items-center gap-2 flex-wrap"><h2>' +
      c.title +
      '</h2><span class="badge badge-tone">' +
      c.badge +
      "</span></div>" +
      '<p class="text-sm text-muted">' +
      c.desc +
      "</p>" +
      "</div>" +
      "</div>" +
      '<div class="cat-links">' +
      '<span class="note"><span class="material-symbols-outlined icon-sm">' +
      c.noteIcon +
      "</span>" +
      c.note +
      "</span>" +
      '<a href="pages/shop/catalog.html?cat=' +
      c.id +
      '">Xem tất cả (' +
      c.total +
      ') <span class="material-symbols-outlined icon-sm">arrow_forward</span></a>' +
      "</div>" +
      "</div>" +
      '<div class="product-grid">' +
      items.map((p) => cardHTML(p)).join("") +
      "</div>" +
      "</section>"
    );
  }).join("");

  /* ---------------- Giỏ hàng ---------------- */
  const CART_KEY = "hv_cart_count";
  const cartBadge = $("#cartCount");
  function readCart() {
    try {
      return parseInt(localStorage.getItem(CART_KEY), 10) || 0;
    } catch (e) {
      return 0;
    }
  }
  function saveCart(n) {
    try {
      localStorage.setItem(CART_KEY, n);
    } catch (e) {
      /* trình duyệt chặn localStorage */
    }
  }
  let cartCount = readCart();
  function renderCart() {
    cartBadge.textContent = cartCount;
    cartBadge.classList.toggle("hidden", cartCount === 0);
  }
  renderCart();

  /* ---------------- Modal ---------------- */
  function openModal(id) {
    $("#" + id).classList.add("is-open");
    document.body.classList.add("modal-open");
  }
  function closeModal(backdrop) {
    backdrop.classList.remove("is-open");
    if (!document.querySelector(".modal-backdrop.is-open"))
      document.body.classList.remove("modal-open");
  }

  /* ---------------- Trả giá ---------------- */
  let offerProduct = null;
  function openOffer(p) {
    offerProduct = p;
    $("#offerProduct").textContent = p.short || p.name;
    $("#offerSeller").textContent = p.sellerName || "-";
    $("#offerCond").textContent = p.cond + "%";
    $("#offerCurrent").textContent = fmt(p.price);
    $("#offerPrice").value = Math.round(p.price * 0.95).toLocaleString("vi-VN");
    $("#offerMsg").value = "";
    openModal("offerModal");
  }

  $("#offerForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const value = parseInt($("#offerPrice").value.replace(/\D/g, ""), 10) || 0;
    if (value <= 0) {
      showPopup({
        type: "error",
        title: "Giá chưa hợp lệ",
        message: "Vui lòng nhập mức giá đề xuất lớn hơn 0.",
        confirmText: "Nhập lại",
      });
      return;
    }
    closeModal($("#offerModal"));
    showPopup({
      type: "success",
      title: "Đã gửi đề nghị trả giá",
      message:
        "Bạn đề nghị " +
        fmt(value) +
        ' cho "' +
        (offerProduct.short || offerProduct.name) +
        '". Hãy chờ người bán phản hồi.',
      confirmText: "Đóng",
    });
  });

  /* ---------------- Đăng bán nhanh ---------------- */
  $("#postForm").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!Auth.ensureLogin(() => {}, {
      title: "Đăng Bán Đồ Cũ",
      message: "Vui lòng đăng nhập tài khoản người bán để đăng tin thanh lý đồ cũ.",
      returnUrl: "pages/seller/post_item.html"
    })) {
      return;
    }
    const name = $("#postName").value.trim();
    const price = parseInt($("#postPrice").value, 10) || 0;
    if (!name || price <= 0) {
      showPopup({
        type: "error",
        title: "Thiếu thông tin",
        message: !name
          ? "Vui lòng nhập tên thiết bị cần đăng bán."
          : "Vui lòng nhập giá muốn bán.",
        confirmText: "Nhập lại",
      });
      return;
    }
    closeModal($("#postModal"));
    e.target.reset();
    showPopup({
      type: "success",
      title: "Đã nhận sản phẩm",
      message: '"' + name + '" đã được đưa vào hàng chờ kiểm duyệt.',
      confirmText: "Đóng",
    });
  });

  /* ---------------- Một chỗ xử lý mọi cú nhấp ---------------- */
  document.addEventListener("click", (e) => {
    // Bấm nền tối của modal -> đóng
    if (e.target.matches("#offerModal, #postModal")) {
      closeModal(e.target);
      return;
    }

    const t = e.target.closest(
      "[data-action],[data-open],[data-close],[data-quick]",
    );
    if (!t) return;

    if (t.dataset.open) {
      if (t.dataset.open === "postModal") {
        if (!Auth.ensureLogin(() => {
          openModal("postModal");
        }, {
          title: "Đăng Bán Đồ Cũ",
          message: "Vui lòng đăng nhập tài khoản người bán để đăng bán đồ cũ.",
          returnUrl: "pages/seller/post_item.html"
        })) {
          return;
        }
      }
      openModal(t.dataset.open);
      return;
    }
    if (t.hasAttribute("data-close")) {
      closeModal(t.closest(".modal-backdrop"));
      return;
    }
    if (t.dataset.quick) {
      if (offerProduct) {
        const v = Math.round(
          offerProduct.price * (1 + Number(t.dataset.quick) / 100),
        );
        $("#offerPrice").value = v.toLocaleString("vi-VN");
      }
      return;
    }

    const p = findProduct(t.dataset.id);
    if (!p) return;
    const title = p.short || p.name;

    if (t.dataset.action === "offer") {
      if (!Auth.ensureLogin(() => {
        openOffer(p);
      }, {
        title: "Yêu Cầu Đăng Nhập",
        message: 'Vui lòng đăng nhập tài khoản để gửi đề nghị trả giá cho "' + title + '".',
      })) {
        return;
      }
      openOffer(p);
    } else if (t.dataset.action === "add-cart") {
      if (!Auth.ensureLogin(() => {
        if (typeof Utils !== "undefined" && Utils.Cart) {
          Utils.Cart.addItem(p, 1);
        } else {
          cartCount++;
          saveCart(cartCount);
          renderCart();
          if (typeof toast === "function") {
            toast('Đã thêm "' + title + '" vào giỏ hàng.', "success");
          }
        }
      }, {
        title: "Đăng Nhập Mua Hàng",
        message: 'Vui lòng đăng nhập tài khoản để thêm "' + title + '" vào giỏ hàng.',
      })) {
        return;
      }
    } else if (t.dataset.action === "buy") {
      if (!Auth.ensureLogin(() => {
        if (typeof Utils !== "undefined" && Utils.Cart) {
          Utils.Cart.addItem(p, 1);
        }
        window.location.href = "pages/shop/cart.html";
      }, {
        title: "Đăng Nhập Mua Hàng",
        message: 'Vui lòng đăng nhập tài khoản để mua ngay "' + title + '".',
        returnUrl: "pages/shop/cart.html"
      })) {
        return;
      }
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    document
      .querySelectorAll("#offerModal.is-open, #postModal.is-open")
      .forEach(closeModal);
  });
})();
