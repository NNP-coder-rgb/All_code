/**
 * utils.js — Root proxy pointing to canonical frontend/js/utils.js
 * Giúp tương thích khi require('./utils.js') trực tiếp tại thư mục gốc dự án.
 */

if (typeof module !== "undefined" && module.exports) {
  module.exports = require("./frontend/js/utils.js");
}
