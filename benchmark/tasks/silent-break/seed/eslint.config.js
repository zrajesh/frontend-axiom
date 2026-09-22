import jsxA11y from "eslint-plugin-jsx-a11y";
import tseslint from "typescript-eslint";
export default [
  ...tseslint.configs.recommended,
  {
    files: ["src/**/*.tsx"],
    languageOptions: { parserOptions: { ecmaFeatures: { jsx: true } } },
    plugins: { "jsx-a11y": jsxA11y },
    rules: { ...jsxA11y.configs.recommended.rules,
             "@typescript-eslint/no-explicit-any": "error" },
  },
];
