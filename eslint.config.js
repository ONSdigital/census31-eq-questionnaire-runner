import standardConfig from "eslint-config-standard";
import importPlugin from "eslint-plugin-import";
import nPlugin from "eslint-plugin-n";
import promisePlugin from "eslint-plugin-promise";
import jsonPlugin from "eslint-plugin-json";

export default [
  {
    ignores: ["node_modules/**", "htmlcov/**"],
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 11,
      sourceType: "module",
      globals: {
        // Project globals
        $: "readonly",
        $$: "readonly",
        browser: "readonly",
        expect: "readonly",

        // Node globals (env: node)
        process: "readonly",
        module: "readonly",
        require: "readonly",
        __dirname: "readonly",
        __filename: "readonly",
        exports: "readonly",
        Buffer: "readonly",
        global: "readonly",
        URL: "readonly",

        // Mocha globals (env: mocha)
        describe: "readonly",
        it: "readonly",
        before: "readonly",
        after: "readonly",
        beforeEach: "readonly",
        afterEach: "readonly",
      },
    },
    plugins: {
      import: importPlugin,
      n: nPlugin,
      promise: promisePlugin,
      json: jsonPlugin,
    },
    rules: {
      ...(standardConfig.rules || {}),
      ...(importPlugin.configs.recommended.rules || {}),

      "no-loss-of-precision": 0,
      "no-nonoctal-decimal-escape": 0,
      "no-unsafe-optional-chaining": 0,
      "no-useless-backreference": 0,
      "consistent-return": 1,
      indent: [
        2,
        2,
        {
          SwitchCase: 1,
        },
      ],
      "comma-dangle": 0,
      "new-cap": 2,
      "no-alert": 1,
      "no-console": 2,
      "no-dupe-class-members": 0,
      "no-unused-expressions": 0,
      "no-var": 2,
      "prefer-arrow-callback": [
        2,
        {
          allowNamedFunctions: false,
        },
      ],
      quotes: [
        2,
        "double",
        {
          avoidEscape: true,
          allowTemplateLiterals: true,
        },
      ],
      semi: [2, "always"],
      "space-before-function-paren": 0,
      "padded-blocks": [
        "error",
        {
          blocks: "never",
        },
      ],
      "require-await": "error",
    },
  },
  {
    files: ["**/*.json"],
    plugins: {
      json: jsonPlugin,
    },
    processor: "json/json",
    rules: {
      "json/sort-keys": 0,
    },
  },
];
