// login.js — xử lý đăng nhập mật khẩu, đăng nhập Google, SMS OTP và khôi phục mật khẩu
(function () {
  const isSubpage = typeof window !== "undefined" && window.location.pathname.includes("/pages/");
  const HOME_PAGE = isSubpage ? "../../index.html" : "index.html";
  const SELLER_PAGE = isSubpage ? "../seller/dashboard.html" : "pages/seller/dashboard.html";
  const ADMIN_PAGE = isSubpage ? "../admin/admin_system.html" : "pages/admin/admin_system.html";

  // Hàm xác định đích đến mặc định theo vai trò tài khoản (Role-based Navigation)
  function getRoleDefaultTarget(user, selectedRole) {
    const roleVal = ((user && user.role) || selectedRole || "buyer").toLowerCase();
    if (roleVal === "seller") return SELLER_PAGE;
    if (roleVal === "admin") return ADMIN_PAGE;
    return HOME_PAGE;
  }

  // Hàm lấy nhãn nút xác nhận trên popup thông báo
  function getConfirmButtonLabel(explicitTarget, user, selectedRole) {
    if (explicitTarget && explicitTarget !== HOME_PAGE && explicitTarget !== SELLER_PAGE && explicitTarget !== ADMIN_PAGE) {
      return "Tiếp tục";
    }
    const roleVal = ((user && user.role) || selectedRole || "buyer").toLowerCase();
    if (roleVal === "seller") return "Vào Kênh Người Bán";
    if (roleVal === "admin") return "Vào Cổng Quản Trị";
    return "Vào trang chủ";
  }

  // Thông điệp chào mừng tương ứng theo vai trò
  function getWelcomeMessage(user, selectedRole) {
    const name = (user && (user.fullName || user.username)) || "bạn";
    const roleVal = ((user && user.role) || selectedRole || "buyer").toLowerCase();
    if (roleVal === "seller") {
      return `Chào mừng Người Bán ${name} quay lại Kênh Quản Lý Gian Hàng!`;
    }
    if (roleVal === "admin") {
      return `Chào mừng Quản trị viên ${name} quay lại Master Admin Portal!`;
    }
    return `Chào mừng ${name} quay lại mua sắm tại Hybrid Store.`;
  }

  // Elements: Form đăng nhập mật khẩu
  const form = document.getElementById("vaultLoginForm");
  const idInput = document.getElementById("identifier");
  const pwd = document.getElementById("vaultKey");
  const pwdIcon = document.getElementById("passwordIcon");
  const btnText = document.getElementById("buttonText");
  const submitBtn = document.getElementById("submitUnlockBtn");
  const submitIcon = document.getElementById("submitIcon");

  // Elements: Tab chuyển đổi phương thức đăng nhập
  const tabLoginPassword = document.getElementById("tabLoginPassword");
  const tabLoginPhone = document.getElementById("tabLoginPhone");
  const phoneOtpLoginForm = document.getElementById("phoneOtpLoginForm");

  // Elements: Phone OTP login
  const otpPhoneNumber = document.getElementById("otpPhoneNumber");
  const btnSendPhoneOtp = document.getElementById("btnSendPhoneOtp");
  const phoneOtpHintBox = document.getElementById("phoneOtpHintBox");
  const phoneOtpDisplayCode = document.getElementById("phoneOtpDisplayCode");
  const phoneOtpCode = document.getElementById("phoneOtpCode");
  const phoneInputError = document.getElementById("phoneInputError");
  const phoneOtpCodeError = document.getElementById("phoneOtpCodeError");
  const submitPhoneOtpBtn = document.getElementById("submitPhoneOtpBtn");

  // Elements: Google Login & Account Management
  const btnGoogleLogin = document.getElementById("btnGoogleLogin");
  const googleLoginBtnText = document.getElementById("googleLoginBtnText");
  const browserGoogleEmailDisplay = document.getElementById("browserGoogleEmailDisplay");
  const googleAccountStatus = document.getElementById("googleAccountStatus");
  const btnSwitchGoogleAccount = document.getElementById("btnSwitchGoogleAccount");

  // Elements: Google Modal
  const googleAuthModal = document.getElementById("googleAuthModal");
  const btnCloseGoogleModal = document.getElementById("btnCloseGoogleModal");
  const currentBrowserGoogleCard = document.getElementById("currentBrowserGoogleCard");
  const modalGoogleAvatar = document.getElementById("modalGoogleAvatar");
  const modalGoogleName = document.getElementById("modalGoogleName");
  const modalGoogleEmail = document.getElementById("modalGoogleEmail");
  const btnConfirmCurrentGoogle = document.getElementById("btnConfirmCurrentGoogle");
  const customGoogleEmail = document.getElementById("customGoogleEmail");
  const customGoogleName = document.getElementById("customGoogleName");
  const rememberCustomGoogle = document.getElementById("rememberCustomGoogle");
  const btnSubmitCustomGoogle = document.getElementById("btnSubmitCustomGoogle");

  // Elements: Forgot Password Modal & Wizard Steps
  const linkForgotPassword = document.getElementById("linkForgotPassword");
  const forgotPasswordModal = document.getElementById("forgotPasswordModal");
  const btnCloseForgotModal = document.getElementById("btnCloseForgotModal");
  const btnCancelForgotModal = document.getElementById("btnCancelForgotModal");
  const forgotStep1 = document.getElementById("forgotStep1");
  const forgotStep2 = document.getElementById("forgotStep2");
  const forgotStep3 = document.getElementById("forgotStep3");
  const forgotIdentifier = document.getElementById("forgotIdentifier");
  const btnSendForgotOtp = document.getElementById("btnSendForgotOtp");
  const forgotStep1Error = document.getElementById("forgotStep1Error");
  const forgotOtpHintBox = document.getElementById("forgotOtpHintBox");
  const forgotOtpDisplayCode = document.getElementById("forgotOtpDisplayCode");
  const forgotOtpCode = document.getElementById("forgotOtpCode");
  const forgotStep2Error = document.getElementById("forgotStep2Error");
  const btnBackToStep1 = document.getElementById("btnBackToStep1");
  const btnVerifyForgotOtp = document.getElementById("btnVerifyForgotOtp");
  const forgotNewPassword = document.getElementById("forgotNewPassword");
  const forgotConfirmPassword = document.getElementById("forgotConfirmPassword");
  const forgotStep3Error = document.getElementById("forgotStep3Error");
  const btnSubmitNewPassword = document.getElementById("btnSubmitNewPassword");

  // Nếu vừa đăng ký xong: điền sẵn email, đưa con trỏ vào ô mật khẩu
  const prefill = sessionStorage.getItem("hv_prefill");
  if (prefill && idInput) {
    idInput.value = prefill;
    sessionStorage.removeItem("hv_prefill");
    if (pwd) pwd.focus();
  }

  // Lấy đường dẫn chuyển hướng sau đăng nhập (từ query ?redirect= hoặc sessionStorage)
  function getRedirectTarget() {
    try {
      const urlParam = new URLSearchParams(window.location.search).get("redirect");
      if (urlParam) return decodeURIComponent(urlParam);
      const stored = sessionStorage.getItem("hv_redirect_after_login");
      if (stored) return stored;
    } catch (e) {}
    return null;
  }

  const initialRedirect = getRedirectTarget();

  // Đã đăng nhập rồi thì chuyển hướng về trang trước hoặc trang tương ứng theo vai trò
  if (typeof Auth !== "undefined" && Auth.current()) {
    const cur = Auth.current();
    if (initialRedirect) {
      sessionStorage.removeItem("hv_redirect_after_login");
      window.location.href = initialRedirect;
    } else {
      window.location.href = getRoleDefaultTarget(cur);
    }
    return;
  }

  // Helper mở/đóng modal an toàn
  function showModal(modalEl) {
    if (!modalEl) return;
    if (typeof openModal === "function") {
      openModal(modalEl);
    } else {
      modalEl.classList.add("is-open");
      modalEl.style.display = "flex";
      document.body.classList.add("modal-open");
    }
  }

  function hideModal(modalEl) {
    if (!modalEl) return;
    if (typeof closeModal === "function") {
      closeModal(modalEl);
    } else {
      modalEl.classList.remove("is-open");
      modalEl.style.display = "none";
      if (!document.querySelector(".modal-backdrop.is-open")) {
        document.body.classList.remove("modal-open");
      }
    }
  }

  // Thông báo toast an toàn
  function notify(opts) {
    if (typeof toast === "function") {
      toast(opts);
    } else if (typeof window.toast === "function") {
      window.toast(opts);
    }
  }

  // ----- Đóng modal khi bấm ra ngoài hoặc phím Escape -----
  [googleAuthModal, forgotPasswordModal].forEach((m) => {
    if (!m) return;
    m.addEventListener("click", (e) => {
      if (e.target === m) hideModal(m);
    });
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      hideModal(googleAuthModal);
      hideModal(forgotPasswordModal);
    }
  });

  // ----- Hiện / ẩn mật khẩu -----
  const toggleBtn = document.getElementById("togglePasswordBtn");
  if (toggleBtn && pwd && pwdIcon) {
    toggleBtn.addEventListener("click", () => {
      const show = pwd.type === "password";
      pwd.type = show ? "text" : "password";
      pwdIcon.textContent = show ? "visibility_off" : "visibility";
    });
  }

  // ----- Đổi vai trò (Buyer vs Seller) -----
  const roleBtns = document.querySelectorAll("#roleSelector button");
  const BTN_LABEL = {
    buyer: "ĐĂNG NHẬP NGAY",
    seller: "ĐĂNG NHẬP NGƯỜI BÁN",
  };
  let role = "buyer";

  // Đọc role từ URL query (ví dụ ?role=seller khi bấm từ nút "Kênh Người Bán" hoặc sau đăng ký)
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const queryRole = urlParams.get("role");
    if (queryRole === "seller" || queryRole === "buyer") {
      role = queryRole;
    }
  } catch (e) {}

  const roleDestText = document.getElementById("roleDestinationText");
  function updateRoleDestHint(currentRole) {
    if (!roleDestText) return;
    const r = String(currentRole || "buyer").toLowerCase();
    if (r === "seller") {
      roleDestText.innerHTML = 'Sau khi đăng nhập sẽ vào: <strong class="text-warning">Kênh Quản Lý Gian Hàng (Seller Dashboard)</strong>';
    } else if (r === "admin") {
      roleDestText.innerHTML = 'Sau khi đăng nhập sẽ vào: <strong class="text-primary">Master Admin Command Portal</strong>';
    } else {
      roleDestText.innerHTML = 'Sau khi đăng nhập sẽ vào: <strong class="text-secondary">Trang Chủ Mua Sắm (Marketplace)</strong>';
    }
  }

  if (btnText) btnText.textContent = BTN_LABEL[role] || BTN_LABEL.buyer;
  updateRoleDestHint(role);
  roleBtns.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.role === role);
    btn.addEventListener("click", () => {
      roleBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      role = btn.dataset.role;
      if (btnText) btnText.textContent = BTN_LABEL[role];
      updateRoleDestHint(role);
    });
  });

  // Gắn sự kiện cho các chip tài khoản kiểm thử nhanh (Demo Accounts)
  const demoChips = document.querySelectorAll("#demoAccountsChips [data-demo-id]");
  demoChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const demoRole = chip.dataset.demoRole;
      const demoId = chip.dataset.demoId;
      const demoPwd = chip.dataset.demoPwd;

      // Chuyển tab sang Mật khẩu nếu đang ở OTP
      if (tabLoginPassword && tabLoginPassword.click) {
        tabLoginPassword.click();
      }

      // Kích hoạt vai trò tương ứng nếu có nút role
      if (demoRole === "seller" || demoRole === "buyer") {
        role = demoRole;
        roleBtns.forEach((b) => b.classList.toggle("active", b.dataset.role === role));
        if (btnText) btnText.textContent = BTN_LABEL[role];
        updateRoleDestHint(role);
      } else if (demoRole === "admin") {
        updateRoleDestHint("admin");
      }

      if (idInput) idInput.value = demoId;
      if (pwd) pwd.value = demoPwd;
      if (submitBtn) submitBtn.focus();
    });
  });

  // =========================================================================
  // 1. CHUYỂN TAB ĐĂNG NHẬP: MẬT KHẨU vs SỐ ĐIỆN THOẠI OTP
  // =========================================================================
  if (tabLoginPassword && tabLoginPhone && form && phoneOtpLoginForm) {
    tabLoginPassword.addEventListener("click", () => {
      tabLoginPassword.classList.add("active");
      tabLoginPhone.classList.remove("active");
      form.style.display = "block";
      phoneOtpLoginForm.style.display = "none";
      if (idInput) idInput.focus();
    });

    tabLoginPhone.addEventListener("click", () => {
      tabLoginPhone.classList.add("active");
      tabLoginPassword.classList.remove("active");
      form.style.display = "none";
      phoneOtpLoginForm.style.display = "block";
      if (otpPhoneNumber) otpPhoneNumber.focus();
    });
  }

  // =========================================================================
  // 2. FORM ĐĂNG NHẬP BẰNG MẬT KHẨU (FORM GỐC)
  // =========================================================================
  function setError(el, msg) {
    const group = el.closest(".form-group");
    if (group) {
      group.classList.add("has-error");
      const err = group.querySelector(".form-error");
      if (err) err.textContent = msg;
    }
    el.classList.add("is-invalid");
  }

  function clearErrors() {
    form.querySelectorAll(".has-error").forEach((g) => g.classList.remove("has-error"));
    form.querySelectorAll(".is-invalid").forEach((i) => i.classList.remove("is-invalid"));
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    clearErrors();

    let bad = null;
    if (!idInput.value.trim()) {
      setError(idInput, "Vui lòng nhập email hoặc số điện thoại.");
      bad = bad || idInput;
    }
    if (!pwd.value) {
      setError(pwd, "Vui lòng nhập mật khẩu.");
      bad = bad || pwd;
    }
    if (bad) {
      bad.focus();
      return;
    }

    const oldText = btnText.textContent;
    submitBtn.disabled = true;
    submitIcon.textContent = "sync";
    submitIcon.classList.add("spin");
    btnText.textContent = "ĐANG ĐĂNG NHẬP...";

    setTimeout(async () => {
      submitBtn.disabled = false;
      submitIcon.classList.remove("spin");
      submitIcon.textContent = "lock_open";
      btnText.textContent = oldText;

      let res;
      // 1. Thử gọi API Backend FastAPI nếu có
      if (typeof API !== "undefined" && API.Auth) {
        try {
          const apiRes = await API.Auth.login(idInput.value.trim(), pwd.value);
          if (apiRes && apiRes.success && apiRes.data) {
            const u = apiRes.data.user;
            res = {
              ok: true,
              user: {
                id: u.id,
                fullName: u.full_name,
                username: u.username,
                email: u.email,
                phone: u.phone,
                role: u.role,
                avatar: u.avatar_url || "assets/images/avatars/default-avatar.svg",
                membershipTitle: u.membership_title || "VIP MEMBER",
                kycStatus: u.is_verified ? "VERIFIED" : "UNVERIFIED"
              }
            };
            localStorage.setItem("hv_current_user", JSON.stringify(res.user));
          }
        } catch (apiErr) {
          console.warn("[Login] API Backend thông báo:", apiErr.message);
        }
      }

      // 2. Dự phòng cục bộ nếu Backend offline
      if (!res) {
        res = Auth.login(idInput.value, pwd.value, role);
      }
      if (!res.ok) {
        if (typeof showPopup === "function") {
          showPopup({
            type: res.warning ? "warning" : "error",
            title: res.warning ? "Chọn lại vai trò" : "Đăng nhập thất bại",
            message: res.error,
            confirmText: "Thử lại",
          });
        } else {
          alert(res.error);
        }
        return;
      }

      if (typeof Utils !== "undefined") {
        if (Utils.Wishlist && typeof Utils.Wishlist.refresh === "function") Utils.Wishlist.refresh();
        if (Utils.Cart) {
          if (typeof Utils.Cart.migrateGuestCart === "function") Utils.Cart.migrateGuestCart();
          if (typeof Utils.Cart.syncBadge === "function") Utils.Cart.syncBadge();
        }
      }

      const targetAfterLogin = getRedirectTarget();
      const destination = targetAfterLogin || getRoleDefaultTarget(res.user, role);
      const confirmLabel = getConfirmButtonLabel(targetAfterLogin, res.user, role);

      if (typeof showPopup === "function") {
        showPopup({
          type: "success",
          title: "Đăng nhập thành công!",
          message: getWelcomeMessage(res.user, role),
          confirmText: confirmLabel,
          onConfirm: () => {
            if (targetAfterLogin) {
              sessionStorage.removeItem("hv_redirect_after_login");
            }
            window.location.href = destination;
          },
        });
      } else {
        if (targetAfterLogin) {
          sessionStorage.removeItem("hv_redirect_after_login");
        }
        window.location.href = destination;
      }
    }, 600);
  });

  // =========================================================================
  // 3. ĐĂNG NHẬP BẰNG TÀI KHOẢN GOOGLE CHUẨN GOOGLE IDENTITY SERVICES (GIS)
  // =========================================================================
  const escapeSafeHtml = (str) =>
    typeof Utils !== "undefined" && Utils.escapeHtml
      ? Utils.escapeHtml(str)
      : String(str || "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");

  function renderGoogleAccountsPicker() {
    const picker = document.getElementById("googleAccountsPicker");
    if (!picker) return;

    picker.innerHTML = "";
    const sampleAccounts = typeof Auth !== "undefined" && typeof Auth.getSampleGoogleAccounts === "function"
      ? Auth.getSampleGoogleAccounts()
      : [];

    const browserAcc = typeof Auth !== "undefined" && typeof Auth.getBrowserGoogleAccount === "function"
      ? Auth.getBrowserGoogleAccount()
      : null;

    const listToRender = [];
    if (browserAcc && browserAcc.email) {
      listToRender.push({
        ...browserAcc,
        isDeviceAccount: true,
        note: "Đang lưu trên thiết bị này"
      });
    }

    sampleAccounts.forEach((acc) => {
      if (!listToRender.some((x) => x.email.toLowerCase() === acc.email.toLowerCase())) {
        listToRender.push(acc);
      }
    });

    listToRender.forEach((acc) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "google-account-row";
      row.innerHTML = `
        <div class="google-avatar-circle">${escapeSafeHtml(acc.avatar || acc.name.slice(0, 2).toUpperCase() || "G")}</div>
        <div class="flex-1 text-left">
          <div class="flex items-center gap-1">
            <strong class="text-xs block" style="color: var(--text);">${escapeSafeHtml(acc.name)}</strong>
            ${acc.isDeviceAccount ? '<span class="badge badge-success" style="font-size: 8px; padding: 1px 5px;">Thiết bị này</span>' : ""}
          </div>
          <span class="text-2xs text-muted block mono">${escapeSafeHtml(acc.email)}</span>
          ${acc.note ? `<span class="text-3xs text-secondary block mt-0.5">${escapeSafeHtml(acc.note)}</span>` : ""}
        </div>
        <span class="material-symbols-outlined icon-xs text-muted">chevron_right</span>
      `;

      row.addEventListener("click", () => {
        row.disabled = true;
        row.style.opacity = "0.7";
        const res = Auth.loginWithGoogle({
          email: acc.email,
          name: acc.name,
          avatar: acc.avatar,
          role: acc.role || role,
        });

        if (res.ok) {
          handleGoogleLoginSuccess(res.user);
        } else {
          notify({
            type: "error",
            title: "Đăng nhập thất bại",
            message: res.error || "Không thể xác thực tài khoản Google.",
          });
          row.disabled = false;
          row.style.opacity = "1";
        }
      });

      picker.appendChild(row);
    });
  }

  function updateGoogleAccountUI() {
    if (typeof Auth === "undefined" || typeof Auth.getBrowserGoogleAccount !== "function") return;
    const browserAcc = Auth.getBrowserGoogleAccount();
    const googleHintRow = document.getElementById("googleHintRow");

    if (browserAcc && browserAcc.email) {
      if (googleLoginBtnText) {
        googleLoginBtnText.innerHTML = `Tiếp tục với Google (<strong>${escapeSafeHtml(browserAcc.email)}</strong>)`;
      }
      if (googleHintRow) googleHintRow.style.display = "flex";
    } else {
      if (googleLoginBtnText) {
        googleLoginBtnText.textContent = "Tiếp tục với tài khoản Google";
      }
      if (googleHintRow) googleHintRow.style.display = "none";
    }
  }

  updateGoogleAccountUI();

  function handleGoogleLoginSuccess(userSession) {
    hideModal(googleAuthModal);
    const targetAfterLogin = getRedirectTarget();
    const destination = targetAfterLogin || getRoleDefaultTarget(userSession, role);
    const confirmLabel = getConfirmButtonLabel(targetAfterLogin, userSession, role);

    if (typeof showPopup === "function") {
      showPopup({
        type: "success",
        title: "Đăng nhập Google thành công!",
        message:
          "Chào mừng " +
          userSession.fullName +
          " (" +
          userSession.email +
          ")! " +
          getWelcomeMessage(userSession, role),
        confirmText: confirmLabel,
        onConfirm: () => {
          if (targetAfterLogin) {
            sessionStorage.removeItem("hv_redirect_after_login");
          }
          window.location.href = destination;
        },
      });
    } else {
      if (targetAfterLogin) {
        sessionStorage.removeItem("hv_redirect_after_login");
      }
      window.location.href = destination;
    }
  }

  if (btnGoogleLogin) {
    btnGoogleLogin.addEventListener("click", () => {
      renderGoogleAccountsPicker();
      showModal(googleAuthModal);
    });
  }

  if (btnSwitchGoogleAccount) {
    btnSwitchGoogleAccount.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      renderGoogleAccountsPicker();
      showModal(googleAuthModal);
    });
  }

  if (btnCloseGoogleModal) {
    btnCloseGoogleModal.addEventListener("click", () => {
      hideModal(googleAuthModal);
    });
  }

  // Nút mở form nhập tài khoản Google khác
  const btnToggleOtherGoogle = document.getElementById("btnToggleOtherGoogle");
  const otherGoogleForm = document.getElementById("otherGoogleForm");
  if (btnToggleOtherGoogle && otherGoogleForm) {
    btnToggleOtherGoogle.addEventListener("click", () => {
      const isHidden = otherGoogleForm.style.display === "none";
      otherGoogleForm.style.display = isHidden ? "block" : "none";
      if (isHidden && customGoogleEmail) customGoogleEmail.focus();
    });
  }

  // Submit form tài khoản Google tự nhập
  if (btnSubmitCustomGoogle && customGoogleEmail) {
    const handleCustomGoogleSubmit = () => {
      const email = customGoogleEmail.value.trim().toLowerCase();
      if (!email || !email.includes("@") || !email.includes(".")) {
        notify({
          type: "warning",
          title: "Email không hợp lệ",
          message: "Vui lòng nhập địa chỉ Email Google hợp lệ (ví dụ: ten-ban@gmail.com).",
        });
        customGoogleEmail.focus();
        return;
      }

      const inputName = customGoogleName ? customGoogleName.value.trim() : "";
      const derivedName = inputName || email.split("@")[0].replace(/[._-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      const avatarInitials = derivedName.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() || "G";

      const newGoogleAcc = {
        email: email,
        name: derivedName,
        avatar: avatarInitials,
        phone: "",
      };

      if (!rememberCustomGoogle || rememberCustomGoogle.checked) {
        Auth.setBrowserGoogleAccount(newGoogleAcc);
        updateGoogleAccountUI();
      }

      const res = Auth.loginWithGoogle({
        ...newGoogleAcc,
        role: role,
      });

      if (res.ok) {
        handleGoogleLoginSuccess(res.user);
      } else {
        notify({
          type: "error",
          title: "Đăng nhập thất bại",
          message: res.error || "Không thể đăng nhập tài khoản Google.",
        });
      }
    };

    btnSubmitCustomGoogle.addEventListener("click", handleCustomGoogleSubmit);
    customGoogleEmail.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleCustomGoogleSubmit();
      }
    });
  }

  // =========================================================================
  // 4. ĐĂNG NHẬP BẰNG SỐ ĐIỆN THOẠI & SMS OTP (BẢO MẬT CAO, CHE MỜ SĐT)
  // =========================================================================
  let phoneOtpCooldownTimer = null;
  const secureSmsNotice = document.getElementById("secureSmsNotice");
  const secureSmsNoticeText = document.getElementById("secureSmsNoticeText");
  const qaSmsBox = document.getElementById("qaSmsBox");
  const btnToggleQaSms = document.getElementById("btnToggleQaSms");
  const qaSmsContent = document.getElementById("qaSmsContent");
  const qaSmsText = document.getElementById("qaSmsText");

  if (btnToggleQaSms && qaSmsContent) {
    btnToggleQaSms.addEventListener("click", () => {
      const isHidden = qaSmsContent.style.display === "none";
      qaSmsContent.style.display = isHidden ? "block" : "none";
    });
  }

  function startPhoneOtpCooldown(seconds) {
    if (!btnSendPhoneOtp) return;
    let remain = seconds;
    btnSendPhoneOtp.disabled = true;
    btnSendPhoneOtp.innerHTML = `<span class="material-symbols-outlined icon-xs spin">sync</span> Gửi lại (${remain}s)`;

    if (phoneOtpCooldownTimer) clearInterval(phoneOtpCooldownTimer);
    phoneOtpCooldownTimer = setInterval(() => {
      remain -= 1;
      if (remain <= 0) {
        clearInterval(phoneOtpCooldownTimer);
        btnSendPhoneOtp.disabled = false;
        btnSendPhoneOtp.innerHTML = `<span class="material-symbols-outlined icon-xs">send</span> Nhận Mã OTP`;
      } else {
        btnSendPhoneOtp.innerHTML = `<span class="material-symbols-outlined icon-xs spin">sync</span> Gửi lại (${remain}s)`;
      }
    }, 1000);
  }

  if (btnSendPhoneOtp && otpPhoneNumber) {
    btnSendPhoneOtp.addEventListener("click", () => {
      if (phoneInputError) phoneInputError.textContent = "";
      const phoneVal = otpPhoneNumber.value.trim();
      const res = Auth.sendPhoneOtp(phoneVal);

      if (!res.ok) {
        if (phoneInputError) phoneInputError.textContent = res.error;
        if (res.remainSeconds) {
          startPhoneOtpCooldown(res.remainSeconds);
        }
        otpPhoneNumber.focus();
        return;
      }

      // Hiển thị thông báo bảo mật che mờ SĐT (KHÔNG in mã OTP lộ thiên ra giao diện chính)
      if (secureSmsNotice && secureSmsNoticeText) {
        secureSmsNotice.style.display = "flex";
        secureSmsNoticeText.innerHTML = `Hệ thống đã gửi mã OTP 6 số đến thuê bao <strong class="text-secondary">${escapeSafeHtml(res.maskedPhone)}</strong>. Mã có hiệu lực trong 3 phút.`;
      }

      // Cập nhật QA Sandbox để kiểm thử viên / stakeholder có thể tra cứu an toàn
      if (qaSmsBox && qaSmsText) {
        qaSmsBox.style.display = "block";
        const smsMsg = Auth.getSimulatedSms(res.phone);
        qaSmsText.textContent = smsMsg || `[HYBRID_AUTH] Mã OTP: ${res.otp} (Hiệu lực 3 phút)`;
      }

      notify({
        type: "info",
        title: "Tin Nhắn SMS Đã Gửi",
        message: `Mã OTP đã gửi đến ${res.maskedPhone}. Vui lòng kiểm tra tin nhắn và nhập mã xác thực.`,
      });

      startPhoneOtpCooldown(60);
      if (phoneOtpCode) {
        phoneOtpCode.value = "";
        phoneOtpCode.focus();
      }
    });
  }

  if (phoneOtpLoginForm) {
    phoneOtpLoginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      if (phoneInputError) phoneInputError.textContent = "";
      if (phoneOtpCodeError) phoneOtpCodeError.textContent = "";

      const phoneVal = otpPhoneNumber ? otpPhoneNumber.value.trim() : "";
      const otpVal = phoneOtpCode ? phoneOtpCode.value.trim() : "";

      if (!phoneVal) {
        if (phoneInputError) phoneInputError.textContent = "Vui lòng nhập số điện thoại.";
        if (otpPhoneNumber) otpPhoneNumber.focus();
        return;
      }

      if (!otpVal || otpVal.length !== 6) {
        if (phoneOtpCodeError) phoneOtpCodeError.textContent = "Vui lòng nhập đúng mã OTP gồm 6 chữ số.";
        if (phoneOtpCode) phoneOtpCode.focus();
        return;
      }

      if (submitPhoneOtpBtn) submitPhoneOtpBtn.disabled = true;

      setTimeout(() => {
        if (submitPhoneOtpBtn) submitPhoneOtpBtn.disabled = false;
        const res = Auth.loginWithPhone(phoneVal, otpVal, role);

        if (!res.ok) {
          if (phoneOtpCodeError) phoneOtpCodeError.textContent = res.error;
          if (typeof showPopup === "function") {
            showPopup({
              type: "error",
              title: "Xác thực OTP thất bại",
              message: res.error,
              confirmText: "Thử lại",
            });
          }
          return;
        }

        if (typeof Utils !== "undefined") {
          if (Utils.Wishlist && typeof Utils.Wishlist.refresh === "function") Utils.Wishlist.refresh();
          if (Utils.Cart) {
            if (typeof Utils.Cart.migrateGuestCart === "function") Utils.Cart.migrateGuestCart();
            if (typeof Utils.Cart.syncBadge === "function") Utils.Cart.syncBadge();
          }
        }

        const targetAfterLogin = getRedirectTarget();
        const destination = targetAfterLogin || getRoleDefaultTarget(res.user, role);
        const confirmLabel = getConfirmButtonLabel(targetAfterLogin, res.user, role);

        if (typeof showPopup === "function") {
          showPopup({
            type: "success",
            title: "Đăng nhập thành công!",
            message:
              "Xác thực số điện thoại " +
              (Auth.maskPhone ? Auth.maskPhone(res.user.phone) : res.user.phone) +
              " thành công. " +
              getWelcomeMessage(res.user, role),
            confirmText: confirmLabel,
            onConfirm: () => {
              if (targetAfterLogin) {
                sessionStorage.removeItem("hv_redirect_after_login");
              }
              window.location.href = destination;
            },
          });
        } else {
          if (targetAfterLogin) {
            sessionStorage.removeItem("hv_redirect_after_login");
          }
          window.location.href = destination;
        }
      }, 400);
    });
  }

  // =========================================================================
  // 5. KHÔI PHỤC MẬT KHẨU QUA EMAIL BẢO MẬT & CẤP MẬT KHẨU MỚI (WIZARD 3 BƯỚC)
  // =========================================================================
  let resetVerifiedEmail = "";
  let generatedNewPassword = "";
  let forgotOtpCooldownTimer = null;

  const wizardBadge1 = document.getElementById("wizardBadge1");
  const wizardBadge2 = document.getElementById("wizardBadge2");
  const wizardBadge3 = document.getElementById("wizardBadge3");
  const forgotMaskedEmailText = document.getElementById("forgotMaskedEmailText");
  const qaEmailBox = document.getElementById("qaEmailBox");
  const btnToggleQaEmail = document.getElementById("btnToggleQaEmail");
  const qaEmailContent = document.getElementById("qaEmailContent");
  const qaEmailText = document.getElementById("qaEmailText");
  const btnResendForgotOtp = document.getElementById("btnResendForgotOtp");
  const displayGeneratedPassword = document.getElementById("displayGeneratedPassword");
  const btnCopyGeneratedPassword = document.getElementById("btnCopyGeneratedPassword");
  const copyPasswordText = document.getElementById("copyPasswordText");
  const copyPasswordIcon = document.getElementById("copyPasswordIcon");
  const btnAutoLoginWithNewPassword = document.getElementById("btnAutoLoginWithNewPassword");

  function setForgotStep(stepIndex) {
    [forgotStep1, forgotStep2, forgotStep3].forEach((step, idx) => {
      if (!step) return;
      if (idx + 1 === stepIndex) {
        step.classList.add("active");
        step.style.display = "block";
      } else {
        step.classList.remove("active");
        step.style.display = "none";
      }
    });

    [wizardBadge1, wizardBadge2, wizardBadge3].forEach((badge, idx) => {
      if (!badge) return;
      badge.classList.toggle("active", idx + 1 === stepIndex);
    });
  }

  function startForgotCooldown(seconds) {
    if (!btnResendForgotOtp) return;
    let remain = seconds;
    btnResendForgotOtp.disabled = true;
    btnResendForgotOtp.innerHTML = `<span class="material-symbols-outlined icon-xs spin">sync</span> Gửi lại (${remain}s)`;

    if (forgotOtpCooldownTimer) clearInterval(forgotOtpCooldownTimer);
    forgotOtpCooldownTimer = setInterval(() => {
      remain -= 1;
      if (remain <= 0) {
        clearInterval(forgotOtpCooldownTimer);
        btnResendForgotOtp.disabled = false;
        btnResendForgotOtp.innerHTML = `<span class="material-symbols-outlined icon-xs">refresh</span> Gửi lại mã`;
      } else {
        btnResendForgotOtp.innerHTML = `<span class="material-symbols-outlined icon-xs spin">sync</span> Gửi lại (${remain}s)`;
      }
    }, 1000);
  }

  if (btnToggleQaEmail && qaEmailContent) {
    btnToggleQaEmail.addEventListener("click", () => {
      const isHidden = qaEmailContent.style.display === "none";
      qaEmailContent.style.display = isHidden ? "block" : "none";
    });
  }

  if (linkForgotPassword) {
    linkForgotPassword.addEventListener("click", () => {
      setForgotStep(1);
      resetVerifiedEmail = "";
      generatedNewPassword = "";
      if (forgotStep1Error) forgotStep1Error.textContent = "";
      if (forgotStep2Error) forgotStep2Error.textContent = "";

      if (forgotIdentifier && idInput && idInput.value.trim()) {
        const val = idInput.value.trim();
        if (val.includes("@")) {
          forgotIdentifier.value = val;
        }
      }

      showModal(forgotPasswordModal);
      if (forgotIdentifier) forgotIdentifier.focus();
    });
  }

  if (btnCloseForgotModal) {
    btnCloseForgotModal.addEventListener("click", () => {
      hideModal(forgotPasswordModal);
    });
  }

  if (btnCancelForgotModal) {
    btnCancelForgotModal.addEventListener("click", () => {
      hideModal(forgotPasswordModal);
    });
  }

  // BƯỚC 1: Gửi mã xác nhận qua Email
  async function triggerSendForgotEmail() {
    if (forgotStep1Error) forgotStep1Error.textContent = "";
    const emailVal = forgotIdentifier ? forgotIdentifier.value.trim().toLowerCase() : "";

    if (!emailVal || !emailVal.includes("@") || !emailVal.includes(".")) {
      if (forgotStep1Error) forgotStep1Error.textContent = "Vui lòng nhập địa chỉ email hợp lệ đã đăng ký.";
      if (forgotIdentifier) forgotIdentifier.focus();
      return;
    }

    if (btnSendForgotOtp) btnSendForgotOtp.disabled = true;

    try {
      let res;
      // Thử gọi qua API backend trước
      if (typeof API !== "undefined" && API.Auth && API.Auth.requestPasswordReset) {
        try {
          const apiRes = await API.Auth.requestPasswordReset(emailVal);
          if (apiRes && apiRes.success && apiRes.data) {
            res = {
              ok: true,
              email: apiRes.data.email,
              maskedEmail: apiRes.data.masked_email,
            };
          }
        } catch (e) {
          console.warn("[Forgot-Password] API fallback sang Auth cục bộ:", e.message);
        }
      }

      if (!res) {
        res = Auth.sendPasswordResetEmail(emailVal);
      }

      if (btnSendForgotOtp) btnSendForgotOtp.disabled = false;

      if (!res.ok) {
        if (forgotStep1Error) forgotStep1Error.textContent = res.error;
        return;
      }

      resetVerifiedEmail = res.email;

      if (forgotMaskedEmailText) {
        forgotMaskedEmailText.textContent = res.maskedEmail || res.email;
      }

      if (qaEmailBox && qaEmailText) {
        qaEmailBox.style.display = "block";
        const emailMsg = Auth.getLastResetEmail(res.email);
        qaEmailText.textContent = emailMsg || `[Security] Mã OTP: ${res.otp || "******"}`;
      }

      notify({
        type: "success",
        title: "Email Xác Thực Đã Gửi",
        message: `Mã OTP xác thực đã được gửi tới ${res.maskedEmail || res.email}. Vui lòng kiểm tra hòm thư.`,
      });

      setForgotStep(2);
      startForgotCooldown(60);
      if (forgotOtpCode) {
        forgotOtpCode.value = "";
        forgotOtpCode.focus();
      }
    } catch (err) {
      if (btnSendForgotOtp) btnSendForgotOtp.disabled = false;
      if (forgotStep1Error) forgotStep1Error.textContent = err.message || "Lỗi khi gửi email.";
    }
  }

  if (btnSendForgotOtp) {
    btnSendForgotOtp.addEventListener("click", triggerSendForgotEmail);
  }
  if (forgotIdentifier) {
    forgotIdentifier.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        triggerSendForgotEmail();
      }
    });
  }

  // BƯỚC 2: Quay lại đổi email
  if (btnBackToStep1) {
    btnBackToStep1.addEventListener("click", () => {
      setForgotStep(1);
      if (forgotIdentifier) forgotIdentifier.focus();
    });
  }

  // BƯỚC 2: Gửi lại mã
  if (btnResendForgotOtp) {
    btnResendForgotOtp.addEventListener("click", () => {
      if (!resetVerifiedEmail) return;
      const res = Auth.sendPasswordResetEmail(resetVerifiedEmail);
      if (!res.ok) {
        if (forgotStep2Error) forgotStep2Error.textContent = res.error;
        return;
      }

      if (qaEmailText) {
        qaEmailText.textContent = Auth.getLastResetEmail(resetVerifiedEmail);
      }

      notify({
        type: "info",
        title: "Đã gửi lại mã OTP",
        message: `Mã xác thực mới đã được gửi tới ${res.maskedEmail}.`,
      });
      startForgotCooldown(60);
    });
  }

  // BƯỚC 2: Xác minh OTP Email và Cấp Mật Khẩu Mới Tự Động
  async function triggerVerifyAndGeneratePassword() {
    if (forgotStep2Error) forgotStep2Error.textContent = "";
    const code = forgotOtpCode ? forgotOtpCode.value.trim() : "";

    if (!code || code.length !== 6) {
      if (forgotStep2Error) forgotStep2Error.textContent = "Vui lòng nhập đúng mã OTP gồm 6 chữ số.";
      if (forgotOtpCode) forgotOtpCode.focus();
      return;
    }

    if (btnVerifyForgotOtp) btnVerifyForgotOtp.disabled = true;

    try {
      let verifyOk = false;

      // 1. Xác thực qua Backend nếu có
      if (typeof API !== "undefined" && API.Auth && API.Auth.verifyPasswordResetOtp) {
        try {
          const apiRes = await API.Auth.verifyPasswordResetOtp(resetVerifiedEmail, code);
          if (apiRes && apiRes.success) verifyOk = true;
        } catch (e) {
          console.warn("[Verify OTP] API fallback sang Auth cục bộ:", e.message);
        }
      }

      if (!verifyOk) {
        const localCheck = Auth.verifyEmailResetOtp(resetVerifiedEmail, code);
        if (!localCheck.ok) {
          if (btnVerifyForgotOtp) btnVerifyForgotOtp.disabled = false;
          if (forgotStep2Error) forgotStep2Error.textContent = localCheck.error;
          if (forgotOtpCode) forgotOtpCode.focus();
          return;
        }
        verifyOk = true;
      }

      // 2. Xác thực thành công -> Cấp mật khẩu mới ngẫu nhiên và gửi về Email
      let newPwdRes = null;
      if (typeof API !== "undefined" && API.Auth && API.Auth.resetPasswordAndSendNew) {
        try {
          const apiNew = await API.Auth.resetPasswordAndSendNew(resetVerifiedEmail, code);
          if (apiNew && apiNew.success && apiNew.data) {
            newPwdRes = {
              ok: true,
              newPassword: apiNew.data.new_password,
              email: apiNew.data.email,
              maskedEmail: apiNew.data.masked_email,
            };
          }
        } catch (e) {
          console.warn("[Reset Password] API fallback sang Auth cục bộ:", e.message);
        }
      }

      if (!newPwdRes) {
        newPwdRes = Auth.generateAndSendNewPassword(resetVerifiedEmail);
      }

      if (btnVerifyForgotOtp) btnVerifyForgotOtp.disabled = false;

      if (!newPwdRes.ok) {
        if (forgotStep2Error) forgotStep2Error.textContent = newPwdRes.error;
        return;
      }

      generatedNewPassword = newPwdRes.newPassword;

      if (displayGeneratedPassword) {
        displayGeneratedPassword.textContent = generatedNewPassword;
      }

      // Chuyển sang Bước 3 hiển thị mật khẩu mới và nút đăng nhập 1-chạm
      setForgotStep(3);

      notify({
        type: "success",
        title: "Đã Cấp Mật Khẩu Mới",
        message: `Mật khẩu mới đã được gửi về ${newPwdRes.maskedEmail || resetVerifiedEmail}.`,
      });
    } catch (err) {
      if (btnVerifyForgotOtp) btnVerifyForgotOtp.disabled = false;
      if (forgotStep2Error) forgotStep2Error.textContent = err.message || "Lỗi xác thực OTP.";
    }
  }

  if (btnVerifyForgotOtp) {
    btnVerifyForgotOtp.addEventListener("click", triggerVerifyAndGeneratePassword);
  }
  if (forgotOtpCode) {
    forgotOtpCode.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        triggerVerifyAndGeneratePassword();
      }
    });
  }

  // BƯỚC 3: Sao chép mật khẩu mới
  if (btnCopyGeneratedPassword) {
    btnCopyGeneratedPassword.addEventListener("click", () => {
      if (!generatedNewPassword) return;
      try {
        navigator.clipboard.writeText(generatedNewPassword);
        if (copyPasswordText) copyPasswordText.textContent = "Đã sao chép!";
        if (copyPasswordIcon) copyPasswordIcon.textContent = "done";
        setTimeout(() => {
          if (copyPasswordText) copyPasswordText.textContent = "Sao chép";
          if (copyPasswordIcon) copyPasswordIcon.textContent = "content_copy";
        }, 2000);
      } catch (e) {
        alert("Mật khẩu mới của bạn là: " + generatedNewPassword);
      }
    });
  }

  // BƯỚC 3: Tự động điền & Đăng nhập ngay bằng mật khẩu mới
  if (btnAutoLoginWithNewPassword) {
    btnAutoLoginWithNewPassword.addEventListener("click", () => {
      hideModal(forgotPasswordModal);

      // Chuyển sang tab Mật khẩu
      if (tabLoginPassword && tabLoginPassword.click) {
        tabLoginPassword.click();
      }

      // Điền email và mật khẩu mới
      if (idInput) idInput.value = resetVerifiedEmail;
      if (pwd) pwd.value = generatedNewPassword;

      notify({
        type: "info",
        title: "Đang Đăng Nhập",
        message: "Hệ thống đang tự động đăng nhập với mật khẩu mới...",
      });

      // Tự động kích hoạt form submit
      setTimeout(() => {
        if (form) {
          form.dispatchEvent(new Event("submit", { cancelable: true }));
        }
      }, 300);
    });
  }
})();
})();
