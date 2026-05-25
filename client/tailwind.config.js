/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  // important: '#app' 确保所有工具类高于 Element Plus 的无层级 CSS
  // 生成 #app .grid { display: grid } 形式，提升特异性但不破坏 EP 组件
  important: '#app',
  corePlugins: {
    preflight: false,   // 禁用 Preflight，防止与 Element Plus 冲突
  },
  theme: {
    extend: {},
  },
  plugins: [],
}
