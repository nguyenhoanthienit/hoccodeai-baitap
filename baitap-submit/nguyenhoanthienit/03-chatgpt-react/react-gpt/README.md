# React + Vite

## Run the chat app

The Vite development server sends chat requests to Groq from its server-side
middleware. Keep the API key out of frontend code. Create a `.env` file in
the project root and add:

```env
GROQ_API_KEY=your-new-groq-api-key
```

`.env` is ignored by Git. Restart the Vite server after adding or changing the
key, then run `npm run dev`.

If an API key was previously added to frontend code or committed, revoke it and
create a replacement before using the app.

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
