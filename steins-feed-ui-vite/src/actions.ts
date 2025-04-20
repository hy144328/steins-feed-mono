import {
  //Item,
  //Language,
  //LikeStatus,
  //Tag,
  //WallMode,
} from "@/client"
import {
  //languagesFeedsLanguagesGet,
  //rootItemsGet,
  //tagsFeedsTagsGet,
} from "@/client"

//import { authenticate } from "@/auth"

/*
export async function getItemsAction(
  dt_from: Date,
  dt_to: Date,
  languages?: Language[],
  tags?: number[],
  wall_mode?: WallMode,
): Promise<Item[]> {
  await authenticate();

  const resp = await rootItemsGet({
    query: {
      dt_from: dt_from.toISOString(),
      dt_to: dt_to.toISOString(),
      languages: languages,
      tags: tags,
      wall_mode: wall_mode,
    },
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
*/
