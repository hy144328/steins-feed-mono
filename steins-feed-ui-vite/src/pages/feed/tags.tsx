import { useEffect, useState } from "react"
import { useNavigate } from "react-router"

import { Feed, Tag } from "@/client"
import {
  attachTagFeedsFeedFeedIdAttachTagPut,
  createAndAttachTagFeedsFeedFeedIdCreateAndAttachTagPut,
  detachTagFeedsFeedFeedIdDetachTagDelete,
  tagsFeedsTagsGet,
} from "@/client"

import { authenticate, require_login } from "@/auth"

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
}: {
  feed: Feed,
}) {
  const navigate = useNavigate();
  const [allTags, setAllTags] = useState<Tag[]>([]);

  const tags_state = sort_tags(feed.tags);
  const tags_sync_state = feed.tags.map(() => true);
  const alternative_tags_state = allTags.filter(tag_it =>
    !contains_tag(tags_state, tag_it.name)
  );

  useEffect(() => {
    async function loadTags() {
      try {
        setAllTags(await getTags());
      } catch (e) {
        console.log(e);
        require_login(navigate, `/feed/${feed.id}`);
      }
    }

    loadTags();
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);
    const tag_name = (data.get("tag") as string).trim();

    if (!contains_tag(tags_state, tag_name)) {
      const tag = allTags.find(tag_it => tag_it.name === tag_name) ?? {id: -1, name: tag_name};

      if (tag.id > 0) {
        set_tags_state(insert_tag(tags_state, tag));
        set_tags_sync_state(insert_by_mirror_tag(tags_sync_state, tags_state, tag, false));

        attachTag(feed.id, tag.id).then(() => {
          set_tags_sync_state(next_tags_sync_state =>
            replace_by_mirror_tag(next_tags_sync_state, insert_tag(tags_state, tag), tag, true)
          );
        });
      } else {
        setAllTags(insert_tag(allTags, tag));
        set_tags_state(insert_tag(tags_state, tag));
        set_tags_sync_state(insert_by_mirror_tag(tags_sync_state, tags_state, tag, false));

        createAndAttachTag(feed.id, tag_name).then(next_tag => {
          setAllTags(next_all_tags_state =>
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
    detachTag(feed.id, tag.id).then(after_detach);
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

async function getTags(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (resp.error) {
    throw resp.error;
  }

  return resp.data ?? [];
}

async function createAndAttachTag(
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

async function attachTag(
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

async function detachTag(
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
