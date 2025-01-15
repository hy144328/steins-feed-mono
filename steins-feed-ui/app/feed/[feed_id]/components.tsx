"use client"

import { useState } from "react"

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
  const [addedTags, setAddedTags] = useState(tags);

  const displayedTags = addedTags.map(tag_it =>
<span
  key={ tag_it.name }
  className="badge rounded-pill text-bg-primary m-1"
>
  { tag_it.name }
  <i className="bi bi-x"/>
</span>
  );

  return (
<form>
  <div>{ displayedTags }</div>

  <InputWithAutoDropdown
    alternatives = { all_tags.map(tag_it => tag_it.name) }
    name="tag"
    placeholder="Enter tag."
  />
</form>
  )
}

export function InputWithAutoDropdown({
  alternatives,
  name,
  placeholder,
}: {
  alternatives: string[],
  name: string,
  placeholder: string,
}) {
  const items = alternatives.map(altIt =>
<li key={ altIt } className="dropdown-item">{ altIt }</li>
  );

  return (
<div className="dropdown">
  <input
    name={ name }
    placeholder={ placeholder }
    className="form-control mt-3 mb-3"
  />

  <ul className="dropdown-menu show">
    { items }
  </ul>
</div>
  )
}
