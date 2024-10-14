"use client";

import { QueryModel } from "@/api-client";
import createApiClient from "@/lib/getApiClient";
import { useEffect, useState } from "react";
import QueryListItem from "./queryListItem";
import { getSessionId } from "@/lib/getUserId";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Skeleton } from "../ui/skeleton";

export default function QueryList() {
  const api = createApiClient();
  const userId = getSessionId();

  const [isLoading, setIsLoading] = useState(true);
  const [queryItems, setQueryItems] = useState<QueryModel[]>([]);

  // Create a hook to call the API.
  useEffect(() => {
    const fetchData = async () => {
      try {
        if (userId) {
          const request = {
            userId: userId,
          };
          const response = await api.listQueryEndpointListQueryGet(request);
          console.log(response);
          setQueryItems(response);
          setIsLoading(false);
          console.log(`Got data: ${JSON.stringify(response)}`);
        } else {
          console.error("User ID is null");
          setIsLoading(false);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        setIsLoading(false);
      }
    };    
    fetchData();
  }, []);

  let queryElements;
  if (isLoading) {
    queryElements = (
      <div className="space-y-2">
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-full" />
      </div>
    );
  } else {
    queryElements = queryItems.map((queryItem) => {
      return <QueryListItem key={queryItem.queryId} {...queryItem} />;
    });
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Recent Queries</CardTitle>
        <CardDescription>
          Here are queries you've recently submitted.
        </CardDescription>
      </CardHeader>
      <CardContent>{queryElements}</CardContent>
    </Card>
  );
}
