export type XftDateFieldProps = {
  value?: string;
  defaultValue?: string;
  width?: number;
  disabled?: boolean;
  min?: string;
  max?: string;
  onChange?: (value: string) => void;
};

export function XftDateField({
  value,
  defaultValue,
  width = 180,
  disabled = false,
  min,
  max,
  onChange,
}: XftDateFieldProps) {
  return (
    <input
      type="date"
      className="xft-input"
      style={{ width }}
      value={value}
      defaultValue={value === undefined ? defaultValue : undefined}
      disabled={disabled}
      min={min}
      max={max}
      onChange={(event) => onChange?.(event.target.value)}
    />
  );
}
