/**
 * utils.js — Re-export proxy pointing to canonical frontend/js/utils.js
 * Giúp tương thích khi gọi từ thư mục frontend/utils.js hoặc trực tiếp từ root.
 */

if (typeof module !== "undefined" && module.exports) {
  module.exports = require("./js/utils.js");
} else if (typeof window !== "undefined") {
  // Trình duyệt: Nếu chưa tải utils.js từ js/utils.js, tự động nạp
  if (!window.Utils) {
    const s = document.createElement("script");
    s.src = "js/utils.js";
    document.head.appendChild(s);
  }
}
