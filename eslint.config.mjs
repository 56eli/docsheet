// Flat-config entrypoint for ESLint (ESLint 9+).
//
// Scope: the shipped browser code only (docs/app.js + docs/js/*.js modules).
// Browser specs/Node tests are executed by Playwright/Node, which fail loudly
// on undefined references, so linting the delivered frontend is where
// `no-undef` earns its keep: a module-scope variable dropped during a refactor
// (the 019fe8a5 P0 ReferenceError class) is caught here, pre-browser.
export default [
  {
    files: ["docs/app.js", "docs/js/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        // Browser runtime globals used by the shipped frontend.
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        localStorage: "readonly",
        location: "readonly",
        history: "readonly",
        console: "readonly",
        fetch: "readonly",
        AbortController: "readonly",
        URL: "readonly",
        Blob: "readonly",
        TextEncoder: "readonly",
        DataView: "readonly",
        Uint8Array: "readonly",
        Uint32Array: "readonly",
        ArrayBuffer: "readonly",
        requestAnimationFrame: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        matchMedia: "readonly",
        HTMLElement: "readonly",
        Option: "readonly",
        // Third-party globals loaded via pinned CDN <script> tags (Tabulator).
        Tabulator: "readonly",
      },
    },
    rules: {
      "no-undef": "error",
    },
  },
];
