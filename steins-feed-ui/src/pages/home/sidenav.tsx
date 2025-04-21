import { useEffect, useState } from "react"
import { useNavigate } from "react-router"

import { Language, Tag, WallMode } from "@/client"
import { languagesFeedsLanguagesGet, tagsFeedsTagsGet } from "@/client"

import { authenticate } from "@/auth"

import { NavigationSearchParams, toURLSearchParams } from "./util"

export default function SideNav({
  now,
  languages,
  tags,
  wall_mode,
}: NavigationSearchParams) {
  const navigate = useNavigate();

  const re_lang = /lang-([A-Za-z]+)/;
  const re_tag = /tag-([0-9]+)/;

  const [allLanguages, setAllLanguages] = useState<Language[]>([]);
  const [allTags, setAllTags] = useState<Tag[]>([]);

  useEffect(() => {
    async function loadLanguages() {
        setAllLanguages(await getAllLanguages());
    }

    loadLanguages();
  }, []);
  useEffect(() => {
    async function loadTags() {
        setAllTags(await getAllTags());
    }

    loadTags();
  }, []);

  const languages_check = allLanguages.map(lang_it =>
    <SideNavCheckbox
      name={ `lang-${lang_it}` }
      label={ lang_it }
      key={ `lang-${lang_it.toLowerCase()}` }
      checked={ languages.includes(lang_it) }
    />
  );
  const tags_check = allTags.map(tag_it =>
    <SideNavCheckbox
      name={ `tag-${tag_it.id}` }
      label={ tag_it.name }
      key={ `tag-${tag_it.id}` }
      checked={ tags.includes(tag_it.id) }
    />
  );
  const wall_radio = [
    "Classic",
    "Magic",
    "Random",
    "Surprise",
  ].map(wall_it =>
    <SideNavRadio
      name="wall_mode"
      value={ wall_it }
      label={ wall_it }
      key={ `wall-${wall_it}` }
      checked={ wall_it === wall_mode }
    />
  )

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const target = e.target;
    if (!(target instanceof HTMLFormElement)) {
      throw e;
    }

    const data = new FormData(target);

    const now = new Date(data.get("now") as string);
    const languages = Array.from(data.entries()).filter(([k, _]) =>
      re_lang.test(k)
    ).filter(([_, v]) =>
      v === "on"
    ).map(([k, _]) =>
      re_lang.exec(k)![1] as Language
    );
    const tags = Array.from(data.entries()).filter(([k, _]) =>
      re_tag.test(k)
    ).filter(([_, v]) =>
      v === "on"
    ).map(([k, _]) =>
      parseInt(re_tag.exec(k)![1])
    );
    const wall_mode = data.get("wall_mode") as WallMode;

    navigate(`/?${toURLSearchParams({now, languages, tags, wall_mode})}`);
  }

  return (
<div
  id="sidenav-offcanvas"
  className="offcanvas offcanvas-end"
  data-bs-backdrop="static"
  data-bs-scroll="true"
>
  <div className="offcanvas-header">
    <h4 className="offcanvas-title">Filters</h4>
    <button className="btn-close" data-bs-dismiss="offcanvas"/>
  </div>

  <div className="offcanvas-body">
    <form onSubmit={ handleSubmit }>
      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Languages</legend>
        { languages_check }
      </fieldset>

      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Tags</legend>
        { tags_check }
      </fieldset>

      <fieldset style={ {all: "revert"} }>
        <legend style={ {all: "revert"} }>Wall</legend>
        { wall_radio }
      </fieldset>

      <fieldset className="mt-3" style={ {all: "revert"} }>
        <input type="hidden" name="now" value={ now.toISOString() }/>

        <div className="btn-group">
          <input type="submit" className="btn btn-primary" data-bs-dismiss="offcanvas"/>
          <input type="reset" className="btn btn-secondary"/>
        </div>
      </fieldset>
    </form>
  </div>
</div>
  );
}

function SideNavCheckbox({
  name,
  label,
  checked = false,
}: {
  name: string,
  label: string,
  checked?: boolean,
}) {
  return (
<div className="form-check">
  <label className="form-check-label">{ label }</label>
  <input
    type="checkbox"
    name={ name }
    defaultChecked={ checked }
    className="form-check-input"
  />
</div>
  );
}

function SideNavRadio({
  name,
  value,
  label,
  checked = false,
}: {
  name: string,
  value: string,
  label: string,
  checked?: boolean,
}) {
  return (
<div className="form-check">
  <label className="form-check-label">{ label }</label>
  <input
    type="radio"
    name={ name }
    value={ value }
    defaultChecked={ checked }
    className="form-check-input"
  />
</div>
  );
}

async function getAllLanguages(): Promise<Language[]> {
  await authenticate();

  const resp = await languagesFeedsLanguagesGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}

async function getAllTags(): Promise<Tag[]> {
  await authenticate();

  const resp = await tagsFeedsTagsGet();

  if (!resp.data) {
    throw resp.error;
  }

  return resp.data;
}
