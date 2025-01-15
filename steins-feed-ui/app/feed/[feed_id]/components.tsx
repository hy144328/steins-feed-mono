"use client"

import { useRef, useState } from "react"

import { Feed, Language, Tag } from "@client"

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
  tags,
  all_tags,
}: {
  tags: Tag[],
  all_tags: Tag[],
}) {
  const [tags_state, set_tags_state] = useState(tags);
  const [all_tags_state, set_all_tags_state] = useState(all_tags);
  const alternative_tags_state = all_tags_state.filter(tag_it =>
    !tags_state.some(t => (tag_it.name === t.name))
  );

  async function handleClose(tag: Tag) {
    set_tags_state(tags_state.filter(tag_it => (tag_it.name !== tag.name)));
  }

  const displayedTags = tags_state.map(tag_it =>
<span
  key={ tag_it.name }
  className="badge rounded-pill text-bg-primary m-1"
>
  { tag_it.name }
  &nbsp;
  <i
    className="bi bi-x"
    style={ {cursor: "pointer"} }
    onClick={ () => handleClose(tag_it) }
  />
</span>
  );

  return (
<form>
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

export function InputWithAutoDropdown<T>({
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
