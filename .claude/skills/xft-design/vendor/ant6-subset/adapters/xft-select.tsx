export type XftSelectOption = {
  label: string;
  value: string;
};

export type XftSelectProps = {
  options: XftSelectOption[];
  placeholder?: string;
  width?: number;
  value?: string;
  defaultValue?: string;
  disabled?: boolean;
  onValueChange?: (value: string) => void;
};

export function XftSelect({
  options,
  placeholder,
  width = 160,
  value,
  defaultValue = "",
  disabled = false,
  onValueChange,
}: XftSelectProps) {
  return (
    <select
      className="xft-select"
      style={{ width }}
      value={value}
      defaultValue={value === undefined ? defaultValue : undefined}
      disabled={disabled}
      onChange={(event) => onValueChange?.(event.target.value)}
    >
      {placeholder ? <option value="">{placeholder}</option> : null}
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
