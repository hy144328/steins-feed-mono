import { useState } from "react"

import { Feed, Tag } from "@/client"
import {
  attachTagFeedsFeedFeedIdAttachTagPut,
  createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut,
  detachTagFeedsFeedFeedIdDetachTagDelete,
} from "@/client"

import { authenticate } from "@/auth"

import { InputWithAutoDropdown } from "./components"

import {
  contains_tag,
  insert_tag,
  insert_by_mirror_tag,
  remove_tag,
  remove_by_mirror_tag,
  replace_tag,
  replace_by_mirror_tag,
  sort_tags,
} from "./util"

export default function TagsForm({
  feed,
  all_tags,
}: {
  feed: Feed,
  all_tags: Tag[],
}) {
  const [tags_state, set_tags_state] = useState(sort_tags(feed.tags));
  const [tags_sync_state, set_tags_sync_state] = useState(feed.tags.map(() => true));
  const [all_tags_state, set_all_tags_state] = useState(all_tags);
  const alternative_tags_state = all_tags_state.filter(tag_it =>
    !contains_tag(tags_state, tag_it.name)
  );

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);
    const tag_name = (data.get("tag") as string).trim();

    if (!contains_tag(tags_state, tag_name)) {
      const tag = all_tags_state.find(tag_it => tag_it.name === tag_name) ?? {id: -1, name: tag_name};

      if (tag.id > 0) {
        set_tags_state(insert_tag(tags_state, tag));
        set_tags_sync_state(insert_by_mirror_tag(tags_sync_state, tags_state, tag, false));

        attachTagAction(feed.id, tag.id).then(() => {
          set_tags_sync_state(next_tags_sync_state =>
            replace_by_mirror_tag(next_tags_sync_state, insert_tag(tags_state, tag), tag, true)
          );
        });
      } else {
        set_all_tags_state(insert_tag(all_tags_state, tag));
        set_tags_state(insert_tag(tags_state, tag));
        set_tags_sync_state(insert_by_mirror_tag(tags_sync_state, tags_state, tag, false));

        createAndAttachTagAction(feed.id, tag_name).then(next_tag => {
          set_all_tags_state(next_all_tags_state =>
            replace_tag(next_all_tags_state, next_tag)
          );
          set_tags_state(next_tags_state =>
            replace_tag(next_tags_state, next_tag)
          );
          set_tags_sync_state(next_tags_sync_state =>
            replace_by_mirror_tag(next_tags_sync_state, insert_tag(tags_state, next_tag), next_tag, true)
          );
        });
      }
    }

    target.reset();
  }

  const displayedTags = tags_state.map((tag_it, tag_ct) =>
<TagPill
  key={ tag_it.name }
  feed={ feed }
  tag={ tag_it }
  in_sync={ tags_sync_state[tag_ct] }
  before_detach={ () => {
    set_tags_sync_state(replace_by_mirror_tag(tags_sync_state, tags_state, tag_it, false));
  } }
  after_detach={ () => {
    set_tags_state(remove_tag(tags_state, tag_it));
    set_tags_sync_state(remove_by_mirror_tag(tags_sync_state, tags_state, tag_it));
  } }
/>
  );

  return (
<form onSubmit={ handleSubmit }>
  <div>{ displayedTags }</div>

  <InputWithAutoDropdown
    alternatives={ alternative_tags_state }
    name="tag"
    placeholder="Enter tag."
    toString={ arg0 => arg0.name }
  />
</form>
  )
}

function TagPill({
  feed,
  tag,
  in_sync = true,
  before_detach = () => {},
  after_detach = () => {},
}: {
  feed: Feed,
  tag: Tag,
  in_sync?: boolean,
  before_detach?: {(): void},
  after_detach?: {(): void},
}) {
  async function handleClose() {
    before_detach();
    detachTagAction(feed.id, tag.id).then(after_detach);
  }

  return (
<span
  key={ tag.name }
  className={ `badge rounded-pill text-bg-${in_sync ? "primary" : "secondary"} m-1` }
>
  { tag.name }
  &nbsp;
  <i
    className="bi bi-x"
    style={ {cursor: "pointer"} }
    onClick={ in_sync ? handleClose : undefined }
  />
</span>
  );
}

async function createAndAttachTagAction(
  feed_id: number,
  tag_name: string,
): Promise<Tag> {
  await authenticate();

  const resp = await createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut({
    path: {feed_id: feed_id},
    query: {tag_name: tag_name},
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

async function attachTagAction(
  feed_id: number,
  tag_id: number,
) {
  await authenticate();

  const resp = await attachTagFeedsFeedFeedIdAttachTagPut({
    path: {feed_id: feed_id},
    query: {tag_id: tag_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}

async function detachTagAction(
  feed_id: number,
  tag_id: number,
) {
  await authenticate();

  const resp = await detachTagFeedsFeedFeedIdDetachTagDelete({
    path: {feed_id: feed_id},
    query: {tag_id: tag_id},
  });

  if (resp.error) {
    throw resp.error;
  }
}
