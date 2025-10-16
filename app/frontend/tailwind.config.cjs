/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "sans-serif"],
      },
      colors: {
        background: "#f2f2f2",
        primary: "#d2f9e1",
        secondary: "#FFEDD5",
        accent: "#71e4ab",
      },
    },
  },
  plugins: [],
};
