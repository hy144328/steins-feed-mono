import { Item } from "@/client"
import {
  analyzeSummaryItemsAnalyzeSummaryGet,
  analyzeTitleItemsAnalyzeTitleGet,
} from "@/client"

import { authenticate } from "@/auth"
import { wrap_words } from "@/parse"

export default function MagicButton({
  item,
  highlight,
  setHighlight,
  setTitle,
  setSummary,
}: {
  item: Item,
  highlight: boolean,
  setHighlight: (value: boolean) => void,
  setTitle: (value: string) => void,
  setSummary: (value: string | null) => void,
}) {
  function markWord(
    word: string,
    stem: string,
    score: number,
  ): HTMLElement {
    const res = document.createElement("mark");

    res.textContent = word;
    res.setAttribute("data-bs-toggle", "popover");
    res.setAttribute("data-bs-title", stem);
    res.setAttribute("data-bs-content", score.toFixed(2));

    return res;
  }

  async function handleHighlight() {
    if (highlight) {
      setTitle(item.title);
      setSummary(item.summary);
    } else if (item.summary) {
      analyzeTitle(item.id).then(records => {
        const stemmer = Object.fromEntries(records.map(([a, b, _]) => [a, b]));
        const scorer = Object.fromEntries(records.map(([a, _, c]) => [a, c]));
        const title = wrap_words(
          item.title,
          records.filter(([_, __, v]) =>
            Math.abs(v) >= 0.5
          ).map(([k, _]) =>
            k
          ),
          frag => markWord(frag, stemmer[frag], scorer[frag]),
        );
        setTitle(title);
      });

      analyzeSummary(item.id).then(records => {
        const stemmer = Object.fromEntries(records.map(([a, b, _]) => [a, b]));
        const scorer = Object.fromEntries(records.map(([a, _, c]) => [a, c]));
        const summary = wrap_words(
          item.summary!,
          records.filter(([_, __, v]) =>
            Math.abs(v) >= 0.5
          ).map(([k, _]) =>
            k
          ),
          frag => markWord(frag, stemmer[frag], scorer[frag]),
        );
        setSummary(summary);
      });
    }

    setHighlight(!highlight);
  }

  return (
<button className={ `btn btn-outline-${highlight?"primary":"secondary"}` } onClick={ handleHighlight }>
<i className="bi-lightbulb-fill"/>
</button>
  );
};

async function analyzeTitle(
  item_id: number,
): Promise<[string, string, number][]> {
  await authenticate();

  const resp = await analyzeTitleItemsAnalyzeTitleGet({"query": {"item_id": item_id}});

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}

async function analyzeSummary(
  item_id: number,
): Promise<[string, string, number][]> {
  await authenticate();

  const resp = await analyzeSummaryItemsAnalyzeSummaryGet({"query": {"item_id": item_id}});

  if (resp.error) {
    throw resp.error;
  }

  return resp.data;
}
