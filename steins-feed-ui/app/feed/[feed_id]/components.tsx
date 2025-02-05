"use client"

import { useState } from "react"

import { Feed, Language, Tag } from "@client"

import {
  attachTagAction,
  attachUserAction,
  createAndAttachTagAction,
  detachTagAction,
  detachUserAction,
  updateFeedAction,
} from "./actions"
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

export function FeedForm({
  feed,
  all_languages,
  is_admin = false,
}: {
  feed: Feed,
  all_languages: Language[],
  is_admin?: boolean,
}) {
  const languageOptions = [
<option key="null"/>
  ].concat(all_languages.map(lang_it =>
<option key={ lang_it } defaultValue={ lang_it }>{ lang_it }</option>
  ));

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);
    const title = data.get("title") as string;
    const link = data.get("link") as string;
    const language = data.get("language") as Language | null;

    try {
      await updateFeedAction(feed.id, title, link, language);
    } catch(exc) {
      alert("Not an admin.");
      throw exc;
    }
  }

  return (
<form onSubmit={ handleSubmit }>
  <div className="form-floating mt-3 mb-3">
    <input
      name="title"
      defaultValue={ feed.title }
      disabled={ !is_admin }
      className="form-control"
    />
    <label>Title</label>
  </div>

  <div className="form-floating mt-3 mb-3">
    <input
      name="link"
      defaultValue={ feed.link }
      disabled={ !is_admin }
      className="form-control"
    />
    <label>Link</label>
  </div>

  <div className="form-floating mt-3 mb-3">
    <select
      name="language"
      className="form-select"
      defaultValue={ feed.language ? feed.language : undefined }
      disabled={ !is_admin }
    >
      { languageOptions }
    </select>
    <label>Language</label>
  </div>

  <div className="btn-group">
    <input type="submit" className="btn btn-primary"/>
    <input type="reset" className="btn btn-secondary"/>
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

export function DisplayForm({
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
