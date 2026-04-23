// ESLint 9 flat config — TypeScript + Svelte
// Complements svelte-check (typechecking) with lint rules.
import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import globals from 'globals';
import svelteConfig from './svelte.config.js';

export default ts.config(
	js.configs.recommended,
	...ts.configs.recommended,
	...svelte.configs['flat/recommended'],
	{
		languageOptions: {
			globals: {
				...globals.browser,
				...globals.node
			}
		},
		rules: {
			'@typescript-eslint/no-unused-vars': [
				'warn',
				{ argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
			],
			'@typescript-eslint/no-explicit-any': 'warn',
			'no-console': ['warn', { allow: ['warn', 'error', 'info'] }]
		}
	},
	{
		files: ['**/*.svelte', '**/*.svelte.ts', '**/*.svelte.js'],
		languageOptions: {
			parserOptions: {
				projectService: true,
				extraFileExtensions: ['.svelte'],
				parser: ts.parser,
				svelteConfig
			}
		}
	},
	{
		ignores: [
			'node_modules/',
			'.svelte-kit/',
			'build/',
			'dist/',
			'.vercel/',
			'src/autogen_api_agent/**',
			'src/nanoclaw_bot/**',
			'tests/**',
			'scripts/**'
		]
	}
);
