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
