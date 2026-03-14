declare module "hono" {
  export type Handler = (context: Context) => Response | Promise<Response>;

  export class Hono {
    post(path: string, handler: Handler): Hono;
  }

  export interface Context {
    req: {
      param(name: string): string;
      json<T>(): Promise<T>;
    };
    json(value: unknown, status?: number): Response;
  }
}

declare const Bun: {
  write(path: string, data: string | Uint8Array): Promise<number>;
  file(path: string): {
    text(): Promise<string>;
  };
};
