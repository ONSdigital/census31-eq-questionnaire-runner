import js from "@eslint/js";
import standardConfig from "eslint-config-standard";
import importPlugin from "eslint-plugin-import";
import jsonPlugin from "eslint-plugin-json";

export default [
  {
    ignores: ["node_modules/**", "htmlcov/**"],
  },
  {
    files: ["**/*.js", "**/*.json"],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: "module",
      globals: {
        $: "readonly",
        $$: "readonly",
        browser: "readonly",
        expect: "readonly",
        // Mocha globals
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
      json: jsonPlugin,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...standardConfig.rules,
      ...importPlugin.configs.recommended.rules,
      // ESLint v10+ rules (disabled as they may not apply to your codebase)
      "no-loss-of-precision": 0,
      "no-nonoctal-decimal-escape": 0,
      "no-unsafe-optional-chaining": 0,
      "no-useless-backreference": 0,
      // Project-specific rules
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
    rules: {
      "json/sort-keys": 0,
    },
  },
];
