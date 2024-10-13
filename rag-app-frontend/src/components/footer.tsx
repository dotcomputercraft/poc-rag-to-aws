import { Code, FileText, Globe, Home, User, Video } from "lucide-react";
import Link from "next/link";

export default function Footer() {

  return (
    <footer className="w-full max-w-3xl text-sm text-slate-400 mt-4">
    <div className="text-center space-y-2">
      <div className="flex items-center gap-2 justify-center sm:flex-row flex-col">
        <Link href="https://github.com/dotcomputercraft/poc-rag-to-aws/blob/main/image/src/data/source/galaxy-design-client-guide.pdf">
          <div className="flex hover:underline hover:text-slate-700">
            <FileText className="mr-1 h-4 w-4 my-auto" />
            Source PDF
          </div>
        </Link>
        <Link href="https://github.com/dotcomputercraft/poc-rag-to-aws">
          <div className="flex hover:underline hover:text-slate-700">
            <Code className="mr-1 h-4 w-4 my-auto" />
            Project Source Code
          </div>
        </Link>
      </div>
    </div>
  </footer>
);
};

