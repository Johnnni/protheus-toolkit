// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	site: 'https://johnnni.github.io',
	base: '/protheus-toolkit',
	integrations: [
		starlight({
			title: 'protheus-toolkit',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/Johnnni/protheus-toolkit' },
			],
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{
					label: 'Inicio',
					items: [
						{ label: 'Sobre', slug: 'sobre' },
						{ label: 'Instalacao', slug: 'instalacao' },
					],
				},
				{
					label: 'Skills',
					items: [
						{ label: 'Visao Geral', slug: 'skills' },
						{
							label: 'ADVPL/TLPP',
							items: [
								{ label: 'advpl-debugging', slug: 'skills/advpl-debugging' },
								{ label: 'advpl-embedded-sql', slug: 'skills/advpl-embedded-sql' },
								{ label: 'advpl-tlpp-language', slug: 'skills/advpl-tlpp-language' },
								{ label: 'advpl-tlpp-migration', slug: 'skills/advpl-tlpp-migration' },
								{ label: 'tlpp-classes', slug: 'skills/tlpp-classes' },
							],
						},
						{
							label: 'Protheus',
							items: [
								{ label: 'protheus-data-model', slug: 'skills/protheus-data-model' },
								{ label: 'protheus-jobs', slug: 'skills/protheus-jobs' },
								{ label: 'protheus-mvc', slug: 'skills/protheus-mvc' },
								{ label: 'protheus-reports', slug: 'skills/protheus-reports' },
								{ label: 'protheus-rest', slug: 'skills/protheus-rest' },
								{ label: 'protheus-screens', slug: 'skills/protheus-screens' },
								{ label: 'business-modules', slug: 'skills/business-modules' },
							],
						},
						{
							label: 'Qualidade',
							items: [
								{ label: 'code-review', slug: 'skills/code-review' },
								{ label: 'teste-de-mesa', slug: 'skills/teste-de-mesa' },
								{ label: 'probat-testing', slug: 'skills/probat-testing' },
								{ label: 'tir-tests', slug: 'skills/tir-tests' },
							],
						},
					],
				},
				{
					label: 'Comandos',
					items: [
						{ label: 'Slash Commands', slug: 'commands' },
					],
				},
				{
					label: 'Agents',
					items: [
						{ label: 'Agents', slug: 'agents' },
					],
				},
				{
					label: 'Integracoes',
					items: [
						{ label: 'MCP Tools', slug: 'mcp-tools' },
						{ label: 'TDS-CLI', slug: 'tds-cli' },
					],
				},
			],
		}),
	],
});
