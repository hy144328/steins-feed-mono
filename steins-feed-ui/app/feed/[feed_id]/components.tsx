"use client"

import { useState } from "react"

import { Feed, Language, Tag } from "@client"

import { doAttachTag, doCreateAndAttachTag, doDetachTag } from "./actions"
import { contains_tag, insert_tag, remove_tag, remove_by_mirror_tag, replace_by_mirror_tag, sort_tags } from "./util"

export function FeedForm({
  feed,
  all_languages,
  isAdmin = false,
}: {
  feed: Feed,
  all_languages: Language[],
  isAdmin?: boolean,
}) {
  const languageOptions = all_languages.map(lang_it =>
<option key={ lang_it } value={ lang_it }>{ lang_it }</option>
  );

  return (
<form>
  <div className="form-floating mt-3 mb-3">
    <input
      name="title"
      value={ feed.title }
      placeholder="Title"
      disabled={ !isAdmin }
      className="form-control"
    />
    <label>Title</label>
  </div>

  <div className="form-floating mt-3 mb-3">
    <input
      name="link"
      value={ feed.link }
      placeholder="Link"
      disabled={ !isAdmin }
      className="form-control"
    />
    <label>Link</label>
  </div>

  <div className="form-floating mt-3 mb-3">
    <select
      name="language"
      className="form-select"
      defaultValue={ feed.language ? feed.language : undefined }
      disabled={ !isAdmin }
    >
      { languageOptions }
    </select>
    <label>Language</label>
  </div>
</form>
  )
}

export function TagsForm({
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
      let tag = all_tags_state.find(tag_it => tag_it.name === tag_name);

      if (tag) {
        await doAttachTag(feed.id, tag.id);
      } else {
        tag = await doCreateAndAttachTag(feed.id, tag_name);

        set_all_tags_state(insert_tag(all_tags_state, tag));
      }

      set_tags_state(insert_tag(tags_state, tag));
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

function InputWithAutoDropdown<T>({
  alternatives,
  name,
  placeholder,
  toString,
}: {
  alternatives: T[],
  name: string,
  placeholder: string,
  toString: {(arg0: T): string},
}) {
  const datalist_options = alternatives.map(altIt =>
<option key={ toString(altIt) } value={ toString(altIt) }/>
  );

  return (
<div className="dropdown">
  <input
    name={ name }
    list={ name }
    autoComplete="off"
    placeholder={ placeholder }
    className="form-control mt-3 mb-3"
  />

  <datalist id={ name }>
    { datalist_options }
  </datalist>
</div>
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
    doDetachTag(feed.id, tag.id).then(after_detach);
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
