import { tool } from 'ai';
import { z } from 'zod';

export const elysiumTools = {
  calculator: tool({
    description: 'Evaluate a mathematical expression. Use for any math, unit conversions, or calculations.',
    parameters: z.object({
      expression: z.string().describe('The math expression to evaluate, e.g. "2 * (3 + 4)" or "Math.sqrt(144)"'),
    }),
    execute: async ({ expression }) => {
      try {
        const sanitized = expression.replace(/[^0-9+\-*/().,%\s]|(?<![a-zA-Z])(?:Math\.[a-zA-Z]+)/g, (match) => {
          if (match.startsWith('Math.')) return match;
          return '';
        });
        const result = new Function(`"use strict"; return (${expression})`)();
        return { result: String(result), expression };
      } catch (e: any) {
        return { error: e.message, expression };
      }
    },
  }),

  webSearch: tool({
    description: 'Search the web for current information. Use when the user asks about recent events, facts you are unsure about, or anything that benefits from up-to-date data.',
    parameters: z.object({
      query: z.string().describe('The search query'),
    }),
    execute: async ({ query }) => {
      try {
        const url = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`;
        const res = await fetch(url);
        const data = await res.json();

        const results: { title: string; snippet: string; url: string }[] = [];

        if (data.AbstractText) {
          results.push({
            title: data.Heading || query,
            snippet: data.AbstractText,
            url: data.AbstractURL || '',
          });
        }

        if (data.RelatedTopics) {
          for (const topic of data.RelatedTopics.slice(0, 5)) {
            if (topic.Text) {
              results.push({
                title: topic.Text.slice(0, 80),
                snippet: topic.Text,
                url: topic.FirstURL || '',
              });
            }
          }
        }

        if (results.length === 0) {
          return { results: [], message: `No instant results found for "${query}". Try rephrasing.` };
        }

        return { results: results.slice(0, 5), query };
      } catch (e: any) {
        return { error: e.message, query };
      }
    },
  }),

  urlFetch: tool({
    description: 'Fetch and extract text content from a URL. Use when the user provides a link or you need to read a web page.',
    parameters: z.object({
      url: z.string().url().describe('The URL to fetch'),
    }),
    execute: async ({ url: targetUrl }) => {
      try {
        const parsed = new URL(targetUrl);
        const hostname = parsed.hostname.toLowerCase();
        const blockedPatterns = [
          /^localhost$/,
          /^127\./,
          /^10\./,
          /^172\.(1[6-9]|2\d|3[01])\./,
          /^192\.168\./,
          /^169\.254\./,
          /^0\./,
          /^\[::1\]$/,
          /^\[fc/,
          /^\[fd/,
        ];
        if (blockedPatterns.some(p => p.test(hostname)) || parsed.protocol === 'file:') {
          return { error: 'Access to internal/private URLs is not allowed', url: targetUrl };
        }

        const res = await fetch(targetUrl, {
          headers: { 'User-Agent': 'Elysium-AI/1.0' },
          signal: AbortSignal.timeout(10000),
        });
        if (!res.ok) return { error: `HTTP ${res.status}: ${res.statusText}`, url: targetUrl };
        const html = await res.text();
        const text = html
          .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
          .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
          .replace(/<[^>]+>/g, ' ')
          .replace(/\s+/g, ' ')
          .trim()
          .slice(0, 5000);
        return { content: text, url: targetUrl, length: text.length };
      } catch (e: any) {
        return { error: e.message, url: targetUrl };
      }
    },
  }),

  codeExec: tool({
    description: 'Execute a JavaScript code snippet and return the result. Use for computations, data transformations, or demonstrating code behavior.',
    parameters: z.object({
      code: z.string().describe('JavaScript code to execute. Use console.log() for output.'),
    }),
    execute: async ({ code }) => {
      try {
        const logs: string[] = [];
        const mockConsole = { log: (...args: any[]) => logs.push(args.map(String).join(' ')) };
        const fn = new Function('console', `"use strict";\n${code}`);
        const result = fn(mockConsole);
        return {
          output: logs.join('\n'),
          returnValue: result !== undefined ? String(result) : undefined,
        };
      } catch (e: any) {
        return { error: e.message };
      }
    },
  }),
};
