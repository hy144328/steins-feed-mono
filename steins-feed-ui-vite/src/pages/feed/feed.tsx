import { Feed, Language } from "@/client"
import {
  updateFeedFeedsFeedFeedIdUpdateFeedPost,
} from "@/client"

import { authenticate } from "@/auth"

export default function FeedForm({
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
<option key={ lang_it } value={ lang_it }>{ lang_it }</option>
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
      await updateFeed(feed.id, title, link, language);
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
      value={ feed.title }
      disabled={ !is_admin }
      className="form-control"
    />
    <label>Title</label>
  </div>

  <div className="form-floating mt-3 mb-3">
    <input
      name="link"
      value={ feed.link }
      disabled={ !is_admin }
      className="form-control"
    />
    <label>Link</label>
  </div>

  <div className="form-floating mt-3 mb-3">
    <select
      name="language"
      className="form-select"
      value={ feed.language ? feed.language : undefined }
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

async function updateFeed(
  feed_id: number,
  title: string,
  link: string,
  language: Language | null,
): Promise<Feed> {
  await authenticate();

  const resp = await updateFeedFeedsFeedFeedIdUpdateFeedPost({
    path: {feed_id: feed_id},
    query: {
      title: title,
      link: link,
      ...(language ? {language: language}: {}),
    },
  });

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
