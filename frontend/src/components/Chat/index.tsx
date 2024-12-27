//Modules
import gptAvatar from "@/assets/gpt-avatar.svg";
import warning from "@/assets/warning.svg";
import user from "@/assets/user.png";
import { useEffect, useRef } from "react";
import { useChat } from "@/store/chat";
import { useForm } from "react-hook-form";
import { useAutoAnimate } from "@formkit/auto-animate/react";
import { OpenAIApi, Configuration } from "openai";
import { useMutation } from "react-query";
import { BACKEND_URL } from "@/config";

//Components
import { Input } from "@/components/Input";
import { FiSend } from "react-icons/fi";
import { Avatar, IconButton, Spinner, Stack, Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import { Instructions } from "../Layout/Instructions";
import { useAPI } from "@/store/api";

export interface ChatProps {}

interface ChatSchema {
  input: string;
}

export const Chat = ({ ...props }: ChatProps) => {
  const { api } = useAPI();
  const { selectedChat, addMessage, addChat, editChat } = useChat();
  const selectedId = selectedChat?.id,
    selectedRole = selectedChat?.role;

  const hasSelectedChat = selectedChat && selectedChat?.content.length > 0;

  const { register, setValue, handleSubmit } = useForm<ChatSchema>();

  const overflowRef = useRef<HTMLDivElement>(null);
  const updateScroll = () => {
    overflowRef.current?.scrollTo(0, overflowRef.current.scrollHeight);
  };

  const [parentRef] = useAutoAnimate();

  const configuration = new Configuration({
    apiKey: api,
  });

  useEffect(() => {
    updateScroll();
    console.log(selectedChat);
  }, [selectedChat]);

  const openAi = new OpenAIApi(configuration);

  const { mutate, isLoading } = useMutation({
    mutationKey: "prompt",
    mutationFn: async (prompt: string) => {
      try {
        let chat_history =
          selectedChat?.content?.map((msg) => {
            return msg.emitter !== "error"
              ? {
                  role: msg.emitter === "user" ? "human" : "ai",
                  content: msg.message,
                }
              : null;
          }) || [];
        console.log(chat_history)
        //remove nulls in chat_history
        chat_history = chat_history.filter((msg) => msg !== null);
        console.log(chat_history);
        const response = await fetch(BACKEND_URL + "/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
          body: JSON.stringify({
            question: prompt,
            chat_history: chat_history,
          }),
        });
        if (!response.ok) {
          throw { error: { message: "Network response was not ok" } };
        }
        return { data: await response.json(), status: response.status };
      } catch (error) {
        throw { error: { message: "Server Unreachable" } };
      }
    },
  });

  const handleAsk = async ({ input: prompt }: ChatSchema) => {
    updateScroll();
    const sendRequest = async (selectedId: string) => {
      setValue("input", "");

      addMessage(selectedId, {
        emitter: "user",
        message: prompt,
      });

      mutate(prompt, {
        onSuccess({ status, data }, variable) {
          console.log(data, variable);
          if (status === 200) {
            const message = String(data["answer"]);
            addMessage(selectedId, {
              emitter: "gpt",
              message,
            });

            if (selectedRole == "New chat" || selectedRole == undefined) {
              editChat(selectedId, { role: variable });
            }
          }
          updateScroll();
        },
        onError(error) {
          console.log(JSON.stringify(error), ">>>>>>>");
          type Error = {
            error: {
              message: string;
            };
          };
          const e: Error = error as Error;

          const message = e.error.message;
          addMessage(selectedId, {
            emitter: "error",
            message,
          });
          updateScroll();
        },
      });
    };

    if (selectedId) {
      if (prompt && !isLoading) {
        await sendRequest(selectedId);
      }
    } else {
      addChat(sendRequest);
    }
  };

  return (
    <Stack width="full" height="full">
      <Stack
        maxWidth="768px"
        width="full"
        marginX="auto"
        height="85%"
        overflow="auto"
        ref={overflowRef}
      >
        <Stack spacing={2} padding={2} ref={parentRef} height="full">
          {hasSelectedChat ? (
            selectedChat.content.map(({ emitter, message }, key) => {
              const getAvatar = () => {
                switch (emitter) {
                  case "gpt":
                    return gptAvatar;
                  case "error":
                    return warning;
                  default:
                    return user;
                }
              };

              const getMessage = () => {
                if (message.slice(0, 2) == "\n\n") {
                  return message.slice(2, Infinity);
                }

                return message;
              };

              return (
                <Stack
                  key={key}
                  direction="row"
                  padding={4}
                  rounded={8}
                  backgroundColor={
                    emitter == "gpt" ? "blackAlpha.200" : "transparent"
                  }
                  spacing={4}
                >
                  <Avatar name={emitter} src={getAvatar()} />
                  <Text
                    whiteSpace="pre-wrap"
                    marginTop=".75em !important"
                    overflow="hidden"
                  >
                    <ReactMarkdown>{getMessage()}</ReactMarkdown>
                  </Text>
                </Stack>
              );
            })
          ) : (
            <Instructions onClick={(text) => setValue("input", text)} />
          )}
        </Stack>
      </Stack>
      <Stack
        height="20%"
        padding={4}
        backgroundColor="blackAlpha.400"
        justifyContent="center"
        alignItems="center"
        overflow="hidden"
      >
        <Stack maxWidth="768px">
          <Input
            autoFocus={true}
            variant="filled"
            inputRightAddon={
              <IconButton
                aria-label="send_button"
                icon={!isLoading ? <FiSend /> : <Spinner />}
                backgroundColor="transparent"
                onClick={handleSubmit(handleAsk)}
              />
            }
            {...register("input")}
            onSubmit={console.log}
            onKeyDown={(e) => {
              if (e.key == "Enter") {
                handleAsk({ input: e.currentTarget.value });
              }
            }}
          />
          <Text textAlign="center" fontSize="sm" opacity={0.5}>
            Free Research Preview. Our goal is to make AI systems more natural
            and safe to interact with. Your feedback will help us improve.
          </Text>
        </Stack>
      </Stack>
    </Stack>
  );
};
