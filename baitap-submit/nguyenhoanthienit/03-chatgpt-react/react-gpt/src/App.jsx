import { useState } from "react";

// Kiểm tra xem tin nhắn có phải là của bot không
function isBotMessage(chatMessage) {
  return chatMessage.role === "assistant";
}

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Gọi hàm này khi người dùng bấm enter, gửi tin nhắn
  const submitForm = async (e) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;

    const userMessage = { role: "user", content: trimmedMessage };
    const updatedHistory = [...chatHistory, userMessage];
    setChatHistory([
      ...updatedHistory,
      { role: "assistant", content: "Vui lòng chờ bot trả lời..." },
    ]);
    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: updatedHistory }),
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Không thể gửi tin nhắn.");
      }
      if (typeof result.content !== "string") {
        throw new Error("Phản hồi từ máy chủ không hợp lệ.");
      }

      setChatHistory([
        ...updatedHistory,
        { role: "assistant", content: result.content },
      ]);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Đã xảy ra lỗi không xác định.";
      setChatHistory([
        ...updatedHistory,
        { role: "assistant", content: `Lỗi: ${errorMessage}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-100 h-screen flex flex-col">
      <div className="container mx-auto p-4 flex flex-col h-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4">ChatUI với React + OpenAI</h1>

        <form className="flex" onSubmit={submitForm}>
          <input
            type="text"
            placeholder="Tin nhắn của bạn..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-grow p-2 rounded-l border border-gray-300"
          />
          <button
            type="submit"
            disabled={isLoading || !message.trim()}
            className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? "Đang gửi..." : "Gửi tin nhắn"}
          </button>
        </form>

        <div className="flex-grow overflow-y-auto mt-4 bg-white rounded shadow p-4">
          {chatHistory.map((chatMessage, i) => (
            <div
              key={i}
              className={`mb-2 ${
                isBotMessage(chatMessage) ? "text-right" : ""
              }`}
            >
              <p className="text-gray-600 text-sm">
                {isBotMessage(chatMessage) ? "Bot" : "User"}
              </p>
              <p
                className={`p-2 rounded-lg inline-block ${
                  isBotMessage(chatMessage) ? "bg-green-100" : "bg-blue-100"
                }`}
              >
                {chatMessage.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;