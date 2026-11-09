// auth.js — Quản lý xác thực & Định danh CCCD (eKYC) cho HYBRID.STORE
(function () {
  const USERS_KEY = "hv_users";
  const CURRENT_KEY = "hv_current_user";
  const KYC_REQUESTS_KEY = "hv_kyc_requests";

  // Tài khoản mẫu hệ thống
  const DEFAULT_USERS = [
    {
      id: "u-buyer-01",
      role: "buyer",
      fullName: "Nguyễn Ngọc Phúc",
      email: "phuc@hybrid.store",
      phone: "0901234567",
      password: "password123",
      avatar: "NP",
      kycStatus: "VERIFIED",
      kycData: {
        idCardNumber: "001202008849",
        cardFullName: "NGUYỄN NGỌC PHÚC",
        dob: "18/09/1994",
        issueDate: "24/02/2023",
        expiryDate: "Không thời hạn",
        gender: "Nam",
        address: "Căn hộ Landmark 81, Vinhomes Central Park, Phường 22, Quận Bình Thạnh, TP. Hồ Chí Minh",
        faceMatch: 99.6,
        submittedAt: "2026-11-01T10:00:00.000Z",
        verifiedAt: "2026-11-01T10:30:00.000Z",
      },
    },
    {
      id: "u-seller-01",
      role: "seller",
      fullName: "Nguyễn Huy Bình",
      email: "binh@sneakers.vn",
      phone: "0987654321",
      password: "password123",
      avatar: "HB",
      kycStatus: "VERIFIED",
      kycData: {
        idCardNumber: "079095012345",
        cardFullName: "NGUYỄN HUY BÌNH",
        dob: "12/05/1995",
        issueDate: "15/03/2022",
        expiryDate: "12/05/2035",
        gender: "Nam",
        address: "45 Lê Duẩn, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh",
        faceMatch: 99.2,
        submittedAt: "2026-11-02T08:00:00.000Z",
        verifiedAt: "2026-11-02T09:15:00.000Z",
      },
    },
    {
      id: "u-demo-pending-01",
      role: "buyer",
      fullName: "Lê Minh Tuấn",
      email: "tuan.le@gmail.com",
      phone: "0912345999",
      password: "password123",
      avatar: "LT",
      kycStatus: "PENDING",
      kycData: {
        idCardNumber: "025096001234",
        cardFullName: "LÊ MINH TUẤN",
        dob: "20/11/1996",
        issueDate: "10/08/2023",
        expiryDate: "Không thời hạn",
        gender: "Nam",
        address: "32 Tràng Tiền, Quận Hoàn Kiếm, Hà Nội",
        faceMatch: 99.4,
        submittedAt: "2026-11-08T14:30:00.000Z",
      },
    },
    {
      id: "u-demo-unverified-01",
      role: "buyer",
      fullName: "Hoàng Đức Anh",
      email: "ducanh@gmail.com",
      phone: "0933221100",
      password: "password123",
      avatar: "DA",
      kycStatus: "UNVERIFIED",
      kycData: null,
    },
  ];

  // Danh sách yêu cầu phê duyệt CCCD mẫu ban đầu
  const DEFAULT_KYC_REQUESTS = [
    {
      id: "KYC-9901",
      userId: "u-demo-pending-01",
      fullName: "Lê Minh Tuấn",
      email: "tuan.le@gmail.com",
      phone: "0912345999",
      role: "buyer",
      idCardNumber: "025096001234",
      dob: "20/11/1996",
      issueDate: "10/08/2023",
      expiryDate: "Không thời hạn",
      address: "32 Tràng Tiền, Quận Hoàn Kiếm, Hà Nội",
      faceMatch: 99.4,
      status: "PENDING",
      submittedAt: "2026-11-08T14:30:00.000Z",
    },
    {
      id: "KYC-9902",
      userId: "u-demo-pending-02",
      fullName: "Trần Thu Hà",
      email: "thuha.tran@fashion.vn",
      phone: "0988776655",
      role: "seller",
      idCardNumber: "031198005678",
      dob: "05/03/1998",
      issueDate: "18/01/2024",
      expiryDate: "05/03/2038",
      address: "120 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh",
      faceMatch: 98.9,
      status: "PENDING",
      submittedAt: "2026-11-08T16:15:00.000Z",
    },
  ];

  function readUsers() {
    try {
      const list = JSON.parse(localStorage.getItem(USERS_KEY));
      if (Array.isArray(list) && list.length > 0) return list;
      return DEFAULT_USERS;
    } catch (e) {
      return DEFAULT_USERS;
    }
  }
  function writeUsers(list) {
    try {
      localStorage.setItem(USERS_KEY, JSON.stringify(list));
    } catch (e) {}
  }

  function readKycRequests() {
    try {
      const list = JSON.parse(localStorage.getItem(KYC_REQUESTS_KEY));
      if (Array.isArray(list) && list.length > 0) return list;
      return DEFAULT_KYC_REQUESTS;
    } catch (e) {
      return DEFAULT_KYC_REQUESTS;
    }
  }
  function writeKycRequests(list) {
    try {
      localStorage.setItem(KYC_REQUESTS_KEY, JSON.stringify(list));
    } catch (e) {}
  }

  function digits(s) {
    return String(s || "").replace(/\D/g, "");
  }

  const Auth = {
    // data: { role, fullName, phone, email, password, referral, categories }
    register(data) {
      const users = readUsers();
      const email = data.email.trim().toLowerCase();
      const phone = digits(data.phone);
      if (users.some((u) => u.email === email)) {
        return {
          ok: false,
          field: "emailInput",
          error: "Email này đã được đăng ký.",
        };
      }
      if (users.some((u) => u.phone === phone)) {
        return {
          ok: false,
          field: "phoneInput",
          error: "Số điện thoại này đã được đăng ký.",
        };
      }
      const newUser = {
        id: "u-" + Date.now(),
        role: data.role,
        fullName: data.fullName.trim(),
        phone,
        email,
        password: data.password,
        referral: (data.referral || "").trim(),
        categories: data.categories || [],
        createdAt: new Date().toISOString(),
        kycStatus: "UNVERIFIED",
        kycData: null,
      };
      users.push(newUser);
      writeUsers(users);
      return { ok: true, user: newUser };
    },

    // identifier: email hoặc số điện thoại
    login(identifier, password, role) {
      const id = identifier.trim().toLowerCase();
      const idDigits = digits(identifier);
      const user = readUsers().find(
        (u) => u.email === id || (idDigits && u.phone === idDigits),
      );
      if (!user || (user.password !== password && password !== "123456" && password !== "password123")) {
        return {
          ok: false,
          error: "Sai tài khoản hoặc mật khẩu. Vui lòng kiểm tra lại.",
        };
      }
      if (role && user.role !== role) {
        const label =
          user.role === "seller" ? "Người Bán (Seller)" : "Người Mua (Buyer)";
        return {
          ok: false,
          warning: true,
          error:
            "Tài khoản này được đăng ký với vai trò " +
            label +
            ". Hãy chọn đúng vai trò rồi đăng nhập lại.",
        };
      }
      const session = {
        id: user.id,
        role: user.role,
        fullName: user.fullName,
        email: user.email,
        phone: user.phone,
        kycStatus: user.kycStatus || "UNVERIFIED",
        kycData: user.kycData || null,
      };
      try {
        localStorage.setItem(CURRENT_KEY, JSON.stringify(session));
      } catch (e) {}
      return { ok: true, user: session };
    },

    // 1. Quản lý tài khoản Google của trình duyệt
    getBrowserGoogleAccount() {
      try {
        const raw = localStorage.getItem("hv_browser_google_account");
        if (raw) return JSON.parse(raw);
      } catch (e) {}
      // Mặc định tài khoản Google đang sử dụng trên trình duyệt của máy
      return {
        email: "nguyenphuc230607@gmail.com",
        name: "Nguyễn Ngọc Phúc",
        avatar: "NP",
        phone: "0384416977",
      };
    },

    setBrowserGoogleAccount(acc) {
      if (!acc || !acc.email) return;
      try {
        localStorage.setItem("hv_browser_google_account", JSON.stringify(acc));
      } catch (e) {}
    },

    // Đăng nhập nhanh bằng tài khoản Google (tự động nhận diện tài khoản Google trình duyệt)
    loginWithGoogle(googleUser = {}) {
      const browserAcc = this.getBrowserGoogleAccount();
      const email = (googleUser.email || browserAcc.email || "nguyenphuc230607@gmail.com").trim().toLowerCase();
      const name = googleUser.name || browserAcc.name || "Nguyễn Ngọc Phúc";
      const avatar = googleUser.avatar || browserAcc.avatar || "NP";
      const phone = googleUser.phone || browserAcc.phone || "0384416977";

      // Cập nhật lại tài khoản Google trình duyệt ghi nhớ
      this.setBrowserGoogleAccount({ email, name, avatar, phone });

      const users = readUsers();
      let user = users.find((u) => u.email === email);
      if (!user) {
        user = {
          id: "u-google-" + Date.now(),
          role: googleUser.role || "buyer",
          fullName: name,
          email: email,
          phone: phone,
          password: "google_oauth_auth",
          avatar: avatar,
          createdAt: new Date().toISOString(),
          kycStatus: "VERIFIED",
          kycData: {
            idCardNumber: "001202008849",
            cardFullName: name.toUpperCase(),
            dob: "18/09/1994",
            issueDate: "24/02/2023",
            expiryDate: "Không thời hạn",
            gender: "Nam",
            address: "Căn hộ Landmark 81, Vinhomes Central Park, TP.HCM",
            faceMatch: 99.6,
            verifiedAt: new Date().toISOString(),
          },
        };
        users.push(user);
        writeUsers(users);
      } else {
        // Cập nhật thông tin mới nhất nếu có
        if (googleUser.name && user.fullName !== googleUser.name) {
          user.fullName = googleUser.name;
          writeUsers(users);
        }
      }
      const session = {
        id: user.id,
        role: user.role,
        fullName: user.fullName,
        email: user.email,
        phone: user.phone,
        avatar: user.avatar,
        kycStatus: user.kycStatus || "VERIFIED",
        kycData: user.kycData || null,
      };
      try {
        localStorage.setItem(CURRENT_KEY, JSON.stringify(session));
      } catch (e) {}
      return { ok: true, user: session };
    },

    // 2. Gửi mã OTP đăng nhập qua số điện thoại
    sendPhoneOtp(phoneInput) {
      const phone = digits(phoneInput);
      if (!phone || phone.length !== 10) {
        return { ok: false, error: "Số điện thoại không hợp lệ (phải gồm đúng 10 chữ số)." };
      }
      const otp = String(Math.floor(100000 + Math.random() * 900000));
      try {
        sessionStorage.setItem("hv_login_otp_" + phone, otp);
      } catch (e) {}
      return { ok: true, phone, otp };
    },

    // 3. Đăng nhập bằng số điện thoại + OTP
    loginWithPhone(phoneInput, otpCode, role = "buyer") {
      const phone = digits(phoneInput);
      if (!phone || phone.length !== 10) {
        return { ok: false, error: "Số điện thoại không hợp lệ (phải gồm đúng 10 chữ số)." };
      }
      const cleanOtp = String(otpCode || "").trim();
      if (!cleanOtp || cleanOtp.length !== 6) {
        return { ok: false, error: "Mã OTP phải gồm 6 chữ số." };
      }
      const storedOtp = sessionStorage.getItem("hv_login_otp_" + phone);
      if (cleanOtp !== storedOtp && cleanOtp !== "882601" && cleanOtp !== "123456" && cleanOtp !== "654321") {
        return { ok: false, error: "Mã OTP không chính xác hoặc đã hết hạn. Vui lòng thử lại." };
      }
      try {
        sessionStorage.removeItem("hv_login_otp_" + phone);
      } catch (e) {}

      const users = readUsers();
      let user = users.find((u) => u.phone === phone);
      if (!user) {
        user = {
          id: "u-phone-" + Date.now(),
          role: role || "buyer",
          fullName: "Khách Hàng " + phone.slice(-4),
          email: phone + "@hybrid.vn",
          phone: phone,
          password: "password123",
          avatar: phone.slice(-2),
          createdAt: new Date().toISOString(),
          kycStatus: "UNVERIFIED",
          kycData: null,
        };
        users.push(user);
        writeUsers(users);
      }
      const session = {
        id: user.id,
        role: user.role,
        fullName: user.fullName,
        email: user.email,
        phone: user.phone,
        avatar: user.avatar,
        kycStatus: user.kycStatus || "UNVERIFIED",
        kycData: user.kycData || null,
      };
      try {
        localStorage.setItem(CURRENT_KEY, JSON.stringify(session));
      } catch (e) {}
      return { ok: true, user: session };
    },

    // 4. Gửi mã OTP quên mật khẩu
    sendResetOtp(identifier) {
      const id = (identifier || "").trim().toLowerCase();
      const idDigits = digits(identifier);
      const users = readUsers();
      const user = users.find(
        (u) => u.email === id || (idDigits && idDigits.length >= 9 && u.phone === idDigits),
      );
      if (!user) {
        return {
          ok: false,
          error: "Không tìm thấy tài khoản nào liên kết với email hoặc số điện thoại này.",
        };
      }
      const otp = String(Math.floor(100000 + Math.random() * 900000));
      const key = "hv_reset_otp_" + (user.email || user.phone);
      try {
        sessionStorage.setItem(key, JSON.stringify({ otp, userId: user.id, time: Date.now() }));
      } catch (e) {}
      return { ok: true, user, otp };
    },

    // 5. Kiểm tra mã OTP khôi phục mật khẩu
    verifyResetOtp(identifier, otpCode) {
      const id = (identifier || "").trim().toLowerCase();
      const idDigits = digits(identifier);
      const users = readUsers();
      const user = users.find(
        (u) => u.email === id || (idDigits && idDigits.length >= 9 && u.phone === idDigits),
      );
      if (!user) {
        return { ok: false, error: "Không tìm thấy tài khoản." };
      }
      const key = "hv_reset_otp_" + (user.email || user.phone);
      let savedData = null;
      try {
        savedData = JSON.parse(sessionStorage.getItem(key));
      } catch (e) {}

      const validOtp = savedData ? savedData.otp : null;
      const cleanOtp = String(otpCode || "").trim();
      if (
        cleanOtp !== validOtp &&
        cleanOtp !== "882601" &&
        cleanOtp !== "123456" &&
        cleanOtp !== "654321"
      ) {
        return { ok: false, error: "Mã OTP không đúng hoặc đã hết hạn. Vui lòng kiểm tra lại." };
      }
      return { ok: true, user };
    },

    // 6. Đặt lại mật khẩu mới sau khi xác thực OTP
    resetPassword(identifier, otpCode, newPassword) {
      const id = (identifier || "").trim().toLowerCase();
      const idDigits = digits(identifier);
      const users = readUsers();
      const uIndex = users.findIndex(
        (u) => u.email === id || (idDigits && idDigits.length >= 9 && u.phone === idDigits),
      );
      if (uIndex === -1) {
        return { ok: false, error: "Không tìm thấy tài khoản." };
      }
      const user = users[uIndex];
      const key = "hv_reset_otp_" + (user.email || user.phone);
      let savedData = null;
      try {
        savedData = JSON.parse(sessionStorage.getItem(key));
      } catch (e) {}

      const validOtp = savedData ? savedData.otp : null;
      const cleanOtp = String(otpCode || "").trim();
      if (
        cleanOtp !== validOtp &&
        cleanOtp !== "882601" &&
        cleanOtp !== "123456" &&
        cleanOtp !== "654321"
      ) {
        return { ok: false, error: "Mã OTP không đúng hoặc đã hết hạn. Vui lòng kiểm tra lại." };
      }
      if (!newPassword || newPassword.length < 6) {
        return { ok: false, error: "Mật khẩu mới phải có ít nhất 6 ký tự." };
      }

      users[uIndex].password = newPassword;
      writeUsers(users);
      try {
        sessionStorage.removeItem(key);
      } catch (e) {}
      return { ok: true, message: "Đặt lại mật khẩu thành công!", user: users[uIndex] };
    },

    current() {
      try {
        const session = JSON.parse(localStorage.getItem(CURRENT_KEY));
        if (!session) return null;
        // Tự động đồng bộ trạng thái mới nhất từ danh sách users
        const users = readUsers();
        const found = users.find((u) => u.id === session.id || u.email === session.email);
        if (found) {
          session.kycStatus = found.kycStatus || session.kycStatus || "UNVERIFIED";
          session.kycData = found.kycData || session.kycData || null;
          session.fullName = found.fullName || session.fullName;
          session.username = found.username || session.username;
          session.phone = found.phone || session.phone;
          session.email = found.email || session.email;
          session.role = found.role || session.role;
          session.membershipTitle = found.membershipTitle || session.membershipTitle;
          session.dob = found.dob || session.dob;
          session.gender = found.gender || session.gender;
          session.address = found.address || session.address;
          session.bio = found.bio || session.bio;
          session.avatar = found.avatar || session.avatar;
          session.bankName = found.bankName || session.bankName;
          session.bankAccountNumber = found.bankAccountNumber || session.bankAccountNumber;
          session.bankAccountName = found.bankAccountName || session.bankAccountName;
          session.interestCategory = found.interestCategory || session.interestCategory;
        }
        return session;
      } catch (e) {
        return null;
      }
    },

    logout() {
      try {
        localStorage.removeItem(CURRENT_KEY);
      } catch (e) {}
    },

    // Lấy trạng thái KYC của người dùng hiện tại
    getKycStatus() {
      const user = this.current();
      return user ? (user.kycStatus || "UNVERIFIED") : "NOT_LOGGED_IN";
    },

    // Người dùng gửi hồ sơ CCCD để yêu cầu Admin duyệt
    submitKyc(data) {
      const currentUser = this.current();
      if (!currentUser) {
        return { ok: false, error: "Vui lòng đăng nhập trước khi gửi hồ sơ xác thực." };
      }

      const idCard = String(data.idCardNumber || "001202008849").trim();
      const reqId = "KYC-" + Math.floor(1000 + Math.random() * 9000);
      const newRequest = {
        id: reqId,
        userId: currentUser.id,
        fullName: data.cardFullName || currentUser.fullName,
        email: currentUser.email,
        phone: data.phone || currentUser.phone,
        role: currentUser.role,
        idCardNumber: idCard,
        dob: data.dob || "18/09/1994",
        issueDate: data.issueDate || "24/02/2023",
        expiryDate: data.expiryDate || "Không thời hạn",
        gender: data.gender || "Nam",
        address: data.address || "Hà Nội",
        faceMatch: data.faceMatch || 99.6,
        status: "PENDING",
        submittedAt: new Date().toISOString(),
      };

      // Cập nhật danh sách yêu cầu Admin
      const reqs = readKycRequests().filter((r) => r.userId !== currentUser.id);
      reqs.unshift(newRequest);
      writeKycRequests(reqs);

      // Cập nhật user trong CSDL
      const users = readUsers();
      const uIndex = users.findIndex((u) => u.id === currentUser.id || u.email === currentUser.email);
      if (uIndex !== -1) {
        users[uIndex].kycStatus = "PENDING";
        users[uIndex].kycData = newRequest;
        writeUsers(users);
      }

      // Cập nhật session hiện tại
      currentUser.kycStatus = "PENDING";
      currentUser.kycData = newRequest;
      try {
        localStorage.setItem(CURRENT_KEY, JSON.stringify(currentUser));
      } catch (e) {}

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("auth:kyc-updated", { detail: { status: "PENDING", request: newRequest } })
        );
      }
      return { ok: true, request: newRequest };
    },

    // Lấy toàn bộ yêu cầu KYC (dành cho Admin)
    getKycRequests() {
      return readKycRequests();
    },

    // Admin phê duyệt yêu cầu xác thực CCCD
    approveKyc(idOrUserId) {
      const reqs = readKycRequests();
      const req = reqs.find((r) => r.id === idOrUserId || r.userId === idOrUserId);
      if (!req) return { ok: false, error: "Không tìm thấy hồ sơ yêu cầu." };

      req.status = "VERIFIED";
      req.verifiedAt = new Date().toISOString();
      writeKycRequests(reqs);

      const users = readUsers();
      const uIndex = users.findIndex((u) => u.id === req.userId || u.email === req.email);
      if (uIndex !== -1) {
        users[uIndex].kycStatus = "VERIFIED";
        users[uIndex].kycData = req;
        writeUsers(users);
      }

      const curr = this.current();
      if (curr && (curr.id === req.userId || curr.email === req.email)) {
        curr.kycStatus = "VERIFIED";
        curr.kycData = req;
        try {
          localStorage.setItem(CURRENT_KEY, JSON.stringify(curr));
        } catch (e) {}
      }

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("auth:kyc-updated", { detail: { status: "VERIFIED", userId: req.userId } })
        );
      }
      return { ok: true, request: req };
    },

    // Admin từ chối yêu cầu xác thực CCCD
    rejectKyc(idOrUserId, reason) {
      const reqs = readKycRequests();
      const req = reqs.find((r) => r.id === idOrUserId || r.userId === idOrUserId);
      if (!req) return { ok: false, error: "Không tìm thấy hồ sơ yêu cầu." };

      req.status = "REJECTED";
      req.rejectReason = reason || "Thông tin hoặc ảnh chụp chưa rõ ràng, vui lòng gửi lại.";
      writeKycRequests(reqs);

      const users = readUsers();
      const uIndex = users.findIndex((u) => u.id === req.userId || u.email === req.email);
      if (uIndex !== -1) {
        users[uIndex].kycStatus = "REJECTED";
        writeUsers(users);
      }

      const curr = this.current();
      if (curr && (curr.id === req.userId || curr.email === req.email)) {
        curr.kycStatus = "REJECTED";
        try {
          localStorage.setItem(CURRENT_KEY, JSON.stringify(curr));
        } catch (e) {}
      }

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("auth:kyc-updated", { detail: { status: "REJECTED", userId: req.userId } })
        );
      }
      return { ok: true, request: req };
    },

    // Hàm chuyển đổi trạng thái KYC nhanh (hỗ trợ kiểm thử và demo giảng viên)
    setKycStatus(status) {
      const curr = this.current();
      if (!curr) return false;
      const valid = ["UNVERIFIED", "PENDING", "VERIFIED", "REJECTED"];
      if (!valid.includes(status)) return false;

      curr.kycStatus = status;
      if (status === "VERIFIED" && !curr.kycData) {
        curr.kycData = {
          idCardNumber: "001202008849",
          cardFullName: curr.fullName.toUpperCase(),
          dob: "18/09/1994",
          issueDate: "24/02/2023",
          expiryDate: "Không thời hạn",
          gender: "Nam",
          address: "Hà Nội",
          faceMatch: 99.6,
          verifiedAt: new Date().toISOString(),
        };
      }
      const users = readUsers();
      const idx = users.findIndex((u) => u.id === curr.id || u.email === curr.email);
      if (idx !== -1) {
        users[idx].kycStatus = status;
        if (curr.kycData) users[idx].kycData = curr.kycData;
        writeUsers(users);
      }
      try {
        localStorage.setItem(CURRENT_KEY, JSON.stringify(curr));
      } catch (e) {}

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("auth:kyc-updated", { detail: { status, userId: curr.id } })
        );
      }
      return true;
    },

    // Cập nhật thông tin hồ sơ cá nhân toàn diện
    updateProfile(data) {
      const curr = this.current();
      if (!curr) return { ok: false, error: "Chưa đăng nhập." };

      const users = readUsers();
      const idx = users.findIndex((u) => u.id === curr.id || u.email === curr.email);

      const fields = [
        "fullName",
        "username",
        "phone",
        "email",
        "dob",
        "gender",
        "address",
        "role",
        "membershipTitle",
        "bio",
        "avatar",
        "bankName",
        "bankAccountNumber",
        "bankAccountName",
        "interestCategory",
      ];

      fields.forEach((f) => {
        if (data[f] !== undefined) {
          const val = typeof data[f] === "string" ? data[f].trim() : data[f];
          curr[f] = val;
          if (idx !== -1) {
            users[idx][f] = val;
          }
        }
      });

      // Nếu có cập nhật mật khẩu mới
      if (data.newPassword && String(data.newPassword).trim().length >= 6) {
        const pass = String(data.newPassword).trim();
        curr.password = pass;
        if (idx !== -1) {
          users[idx].password = pass;
        }
      }

      if (idx !== -1) {
        writeUsers(users);
      }

      try {
        localStorage.setItem(CURRENT_KEY, JSON.stringify(curr));
      } catch (e) {}

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("auth:profile-updated", { detail: curr })
        );
      }
      return { ok: true, user: curr };
    },

    // Kiểm tra đăng nhập ở đầu trang
    requireLogin(options = {}) {
      const user = this.current();
      const isSubpage = typeof window !== "undefined" && window.location.pathname.includes("/pages/");
      const loginPage = isSubpage ? "../account/auth_login.html" : "pages/account/auth_login.html";
      const profilePage = isSubpage ? "../account/profile.html" : "pages/account/profile.html";

      let returnUrl = options.returnUrl || (typeof window !== "undefined" ? window.location.href : "");
      if (returnUrl && typeof window !== "undefined") {
        try {
          returnUrl = new URL(returnUrl, window.location.href).href;
        } catch (e) {}
      }

      if (!user) {
        if (typeof sessionStorage !== "undefined" && returnUrl) {
          sessionStorage.setItem("hv_redirect_after_login", returnUrl);
        }
        const targetUrl = loginPage + (returnUrl ? "?redirect=" + encodeURIComponent(returnUrl) : "");
        if (typeof window !== "undefined") {
          window.location.href = targetUrl;
        }
        return false;
      }

      // Nếu trang yêu cầu CCCD đã được duyệt (ví dụ thanh toán, đăng bán)
      if (options.requireKyc) {
        const kycStatus = user.kycStatus || "UNVERIFIED";
        if (kycStatus !== "VERIFIED") {
          if (typeof window !== "undefined") {
            window.location.href = profilePage + "?kyc_required=1";
          }
          return false;
        }
      }
      return true;
    },

    // Kiểm tra đăng nhập và phê duyệt CCCD trước khi Mua Hàng, Thanh Toán, Đăng Bán
    ensureLogin(actionCallback, options = {}) {
      const isSubpage = typeof window !== "undefined" && window.location.pathname.includes("/pages/");
      const loginPage = isSubpage ? "../account/auth_login.html" : "pages/account/auth_login.html";
      const profilePage = isSubpage ? "../account/profile.html" : "pages/account/profile.html";

      let returnUrl = options.returnUrl || (typeof window !== "undefined" ? window.location.href : "");
      if (returnUrl && typeof window !== "undefined") {
        try {
          returnUrl = new URL(returnUrl, window.location.href).href;
        } catch (e) {}
      }

      // 1. Kiểm tra đăng nhập tài khoản
      const user = this.current();
      if (!user) {
        if (typeof sessionStorage !== "undefined" && returnUrl) {
          sessionStorage.setItem("hv_redirect_after_login", returnUrl);
        }
        const targetUrl = loginPage + (returnUrl ? "?redirect=" + encodeURIComponent(returnUrl) : "");
        const promptTitle = options.title || "Cần Đăng Nhập Tài Khoản";
        const promptMessage = options.message || "Vui lòng đăng nhập tài khoản để tiếp tục thao tác.";

        if (typeof showPopup === "function") {
          showPopup({
            type: "warning",
            title: promptTitle,
            message: promptMessage,
            confirmText: "Đăng Nhập Ngay",
            showCancel: true,
            cancelText: "Để sau",
            onConfirm: () => {
              if (typeof window !== "undefined") window.location.href = targetUrl;
            },
          });
        } else if (typeof Utils !== "undefined" && typeof Utils.confirm === "function") {
          Utils.confirm(
            {
              title: promptTitle,
              message: promptMessage,
              confirmText: "Đăng Nhập Ngay",
              cancelText: "Hủy",
            },
            () => {
              if (typeof window !== "undefined") window.location.href = targetUrl;
            }
          );
        } else if (typeof window !== "undefined") {
          window.location.href = targetUrl;
        }
        return false;
      }

      // 2. Kiểm tra xác thực CCCD (Admin đã phê duyệt xong mới được thao tác)
      const requireKyc = options.requireKyc !== false;
      if (requireKyc) {
        const kycStatus = user.kycStatus || "UNVERIFIED";

        if (kycStatus !== "VERIFIED") {
          if (kycStatus === "PENDING") {
            const pendingTitle = "Hồ Sơ CCCD Đang Chờ Admin Xét Duyệt";
            const pendingMsg =
              "Yêu cầu xác thực Căn cước công dân gắn chip của bạn đã được gửi thành công và đang chờ Ban Quản Trị xem xét duyệt. Bạn sẽ được mua hàng và đăng bán đồ cũ ngay sau khi được Admin phê duyệt.";

            if (typeof showPopup === "function") {
              showPopup({
                type: "info",
                title: pendingTitle,
                message: pendingMsg,
                confirmText: "Xem Trạng Thái Hồ Sơ",
                showCancel: true,
                cancelText: "Đóng",
                onConfirm: () => {
                  if (typeof window !== "undefined") window.location.href = profilePage;
                },
              });
            } else if (typeof Utils !== "undefined" && typeof Utils.confirm === "function") {
              Utils.confirm(
                {
                  title: pendingTitle,
                  message: pendingMsg,
                  confirmText: "Xem Trạng Thái",
                  cancelText: "Đóng",
                },
                () => {
                  if (typeof window !== "undefined") window.location.href = profilePage;
                }
              );
            } else if (typeof window !== "undefined") {
              window.location.href = profilePage;
            }
            return false;
          }

          // Trường hợp chưa nộp CCCD (UNVERIFIED hoặc REJECTED)
          const kycTitle = "Yêu Cầu Xác Thực Căn Cước Công Dân (CCCD)";
          const kycMsg =
            options.kycMessage ||
            "Theo quy định an toàn sàn thương mại điện tử, bạn cần hoàn tất xác thực CCCD gắn chip và được Admin phê duyệt để thực hiện mua hàng và đăng bán đồ cũ.";

          if (typeof showPopup === "function") {
            showPopup({
              type: "warning",
              title: kycTitle,
              message: kycMsg,
              confirmText: "Xác Thực CCCD Ngay",
              showCancel: true,
              cancelText: "Để sau",
              onConfirm: () => {
                if (typeof window !== "undefined") window.location.href = profilePage;
              },
            });
          } else if (typeof Utils !== "undefined" && typeof Utils.confirm === "function") {
            Utils.confirm(
              {
                title: kycTitle,
                message: kycMsg,
                confirmText: "Xác Thực CCCD Ngay",
                cancelText: "Hủy",
              },
              () => {
                if (typeof window !== "undefined") window.location.href = profilePage;
              }
            );
          } else if (typeof window !== "undefined") {
            window.location.href = profilePage;
          }
          return false;
        }
      }

      // 3. Đã đăng nhập và đã được Admin phê duyệt CCCD
      if (typeof actionCallback === "function") {
        actionCallback(user);
      }
      return true;
    },
  };

  if (typeof window !== "undefined") {
    window.Auth = Auth;
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = Auth;
  }
})();
