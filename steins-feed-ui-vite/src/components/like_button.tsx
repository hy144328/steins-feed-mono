import { useNavigate } from "react-router"

import { authenticate } from "@/auth"
import { Item, LikeStatus } from "@/client"
import { likeItemsLikePut } from "@/client"

export function LikeButton({
  item,
  liked,
  setLiked,
}: {
  item: Item,
  liked: LikeStatus,
  setLiked: (value: LikeStatus) => void,
}) {
  const navigate = useNavigate();

  async function handleLiked() {
    const score = (liked === 1) ? 0 : 1;

    try {
      await putLike(item.id, score);
    } catch(e) {
      console.log(e);
      navigate(0);
    }

    setLiked(score);
  }

  return (
<button className={ `btn btn-outline-${(liked === 1)?"primary":"secondary"}` } onClick={ handleLiked }>
<i className="bi-hand-thumbs-up-fill"/>
</button>
  );
}

export function DislikeButton({
  item,
  liked,
  setLiked,
}: {
  item: Item,
  liked: LikeStatus,
  setLiked: (value: LikeStatus) => void,
}) {
  const navigate = useNavigate();

  async function handleDisliked() {
    const score = (liked === -1) ? 0 : -1;

    try {
      await putLike(item.id, score);
    } catch(e) {
      console.log(e);
      navigate(0);
    }

    setLiked(score);
  }

  return (
<button className={ `btn btn-outline-${(liked === -1)?"primary":"secondary"}` } onClick={ handleDisliked }>
<i className="bi-hand-thumbs-down-fill"/>
</button>
  );
}

async function putLike(item_id: number, score: LikeStatus) {
  await authenticate();

  const resp = await likeItemsLikePut({
    "query": {
      "item_id": item_id,
      "score": score,
    },
  });

  if (resp.error) {
    throw resp.error;
  }
}
