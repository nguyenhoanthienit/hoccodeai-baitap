import { Buffer } from "node:buffer";
import OpenAI from "openai";
import process from "node:process";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import tailwindcss from "@tailwindcss/vite";

function groqChatApi(apiKey) {
  return {
    name: "groq-chat-api",
    configureServer(server) {
      server.middlewares.use("/api/chat", async (req, res) => {
        const sendJson = (statusCode, body) => {
          res.statusCode = statusCode;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify(body));
        };

        if (req.method !== "POST") {
          sendJson(405, { error: "Method not allowed." });
          return;
        }

        if (!apiKey) {
          sendJson(503, {
            error:
              "GROQ_API_KEY is not set. Add it to the project root .env file before starting the dev server.",
          });
          return;
        }

        let body;
        try {
          let rawBody = "";
          for await (const chunk of req) {
            rawBody += chunk;
            if (Buffer.byteLength(rawBody) > 1024 * 1024) {
              sendJson(413, { error: "Request body is too large." });
              return;
            }
          }
          body = JSON.parse(rawBody);
        } catch {
          sendJson(400, { error: "Request body must be valid JSON." });
          return;
        }

        const { messages } = body ?? {};
        if (
          !Array.isArray(messages) ||
          messages.length === 0 ||
          messages.some(
            (message) =>
              !message ||
              !["user", "assistant"].includes(message.role) ||
              typeof message.content !== "string",
          )
        ) {
          sendJson(400, {
            error: "Messages must contain valid user or assistant text.",
          });
          return;
        }

        try {
          const groq = new OpenAI({
            apiKey,
            baseURL: "https://api.groq.com/openai/v1",
          });
          const completion = await groq.chat.completions.create({
            messages,
            model: "openai/gpt-oss-20b",
          });
          const content = completion.choices[0]?.message?.content;
          if (typeof content !== "string") {
            throw new Error("The chat provider returned no message content.");
          }
          sendJson(200, { content });
        } catch (error) {
          console.error("Groq chat request failed:", error);
          sendJson(502, {
            error:
              "The chat provider request failed. Check the server terminal for details.",
          });
        }
      });
    },
  };
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const { GROQ_API_KEY } = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react(), tailwindcss(), groqChatApi(GROQ_API_KEY)],
  };
});
