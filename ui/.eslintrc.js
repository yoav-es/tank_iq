module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 2021,
    sourceType: 'module',
  },
  extends: [
    'airbnb-base',
    'airbnb-typescript/base',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'prettier', // optional if you use Prettier
  ],
  plugins: [
    'vue',
    '@typescript-eslint',
  ],
  rules: {
    // Example overrides
    'import/extensions': 'off', // allow TS imports without extension
    'import/no-extraneous-dependencies': 'off', // handled by tsconfig
    'class-methods-use-this': 'off', // not always useful in Vue components
    'vue/multi-word-component-names': 'off', // allow single-word component names
    '@typescript-eslint/no-unused-vars': ['warn'],
  },
};
