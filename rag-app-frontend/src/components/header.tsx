import { Code, FileText, Globe, Home, User, Video } from "lucide-react";
import Link from "next/link";
import { getApiUrl } from "@/lib/getApiClient";
import { getSessionId } from "@/lib/getUserId";

export default function Header() {

    const userId = getSessionId();
    const truncatedUserId = userId?.slice(0, 8);
    console.log("userId", userId);

    return (
        <>
        <header className="w-full max-w-3xl flex justify-between items-center text-xs">
            <Link href="/">
            <div className="text-slate-600 flex">
                <Home className="my-auto mr-1 h-4 w-4" /> Home
            </div>
            </Link>
            <div className="flex gap-2">
            <div className="bg-slate-300 p-1 rounded-sm text-slate-600 flex">
                <User className="my-auto mr-2 h-4 w-4" /> {truncatedUserId}
            </div>
            <div className="bg-slate-300 p-1 rounded-sm text-slate-600 flex">
                <Globe className="my-auto mr-2 h-4 w-4" /> {getApiUrl()}
            </div>
            </div>
        </header>
        </>
    );
}