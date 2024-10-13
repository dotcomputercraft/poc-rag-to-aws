"use client";

import QueryList from "@/components/app/queryList";
import SubmitQueryForm from "@/components/ui/submitQueryForm";
import Image from "next/image";

export default function Home() {

  return (
    <>
      <SubmitQueryForm></SubmitQueryForm>
      <QueryList></QueryList>
    </>
  );
}
