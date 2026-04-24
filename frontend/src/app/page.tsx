import { ChatWindow } from "@/components/ChatWindow";

export default function HomePage() {
  return (
    <main className="relative flex items-center justify-center min-h-screen overflow-hidden bg-sanctuary">
      {/* Atmospheric orbs */}
      <div className="orb w-[500px] h-[500px] bg-brand/10 top-[-120px] left-[-120px]" />
      <div className="orb w-[400px] h-[400px] bg-sky-500/5 bottom-[-80px] right-[-80px]" />

      {/* Chat container */}
      <div className="relative z-10 w-full max-w-5xl mx-4 h-[88vh] glass rounded-zen overflow-hidden shadow-2xl flex">
        <ChatWindow />
      </div>
    </main>
  );
}
