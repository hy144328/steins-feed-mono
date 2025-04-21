import { Feed } from "@/client"
import {
  attachUserFeedsFeedFeedIdAttachUserPut,
  detachUserFeedsFeedFeedIdDetachUserDelete,
} from "@/client"

import { authenticate } from "@/auth"

export default function DisplayForm({
  feed,
}: {
  feed: Feed,
}) {
  async function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.checked) {
      await attachUserAction(feed.id);
    } else {
      await detachUserAction(feed.id);
    }
  }

  return (
<form>
  <div className="form-check form-switch fs-1">
    <input
      type="checkbox"
      className="form-check-input"
      defaultChecked={ feed.displayed }
      onChange={ handleChange }
    />
    <label className="form-check-label">Feed #{ feed.id }</label>
  </div>
</form>
  );
}

async function attachUserAction(
  feed_id: number,
) {
  await authenticate();

  const resp = await attachUserFeedsFeedFeedIdAttachUserPut({
    path: {feed_id: feed_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}

async function detachUserAction(
  feed_id: number,
) {
  await authenticate();

  const resp = await detachUserFeedsFeedFeedIdDetachUserDelete({
    path: {feed_id: feed_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}
