# Proposed new `sample_service` methods:

Or, at least what the sample landing page is mocking.

Currently the sample  and sample set landing pages are using versions of these methods and data structures, mocked, using data generated from scripts in the refactor2-ui pull request https://github.com/kbase/sample_service_validator_config/pull/38.

## `get_formats`

Returns one or more requested sample format specifiications. 

An example of usage in the UI  is display the format identity in the sample header, includig the correct acronym or short title, the full title as a tooltip, and providing that in a link to the format organization's home page.

Params:

- Ids: - Array<string> - an array of format identifiers (sear, enigma, etc.)

Result:

- Formats: - Array<Format> - an array of sample format specifications, in the same order as requested.

Structures:

- Format:

  ```typescript
  export interface Format {
      name: string;
      info: {
          title: string;
          shortTitle: string;
          homePage: string
      }
      mappings: {
          id: string;
          parent: string;
          name: string;
      },
      columns: Array<FormatColumn>
  }
  
  export interface FormatColumn {
      title: string;
      aliases: Array<string>;
      sampleKey: string;
  }
  ```

## `get_field_groups`

Taking no parameters, returns a definition of field groupings. Field are ordered groupings are ordered lists of field keys. Each field key must appear in only one group.

### `Params`:

- none

### `Result`: 

- Groups - Grouping - a mapping of group id to arrays of field keys.

### `Where`:

- Grouping is

  ```typescript
  export type ControlledFieldKey = string;
  
  export interface FieldGroup {
      name: string;
      title: string;
      fields: Array<ControlledFieldKey>;
  }
  
  export type FieldGroups = Array<FieldGroup>;
  ```

  

## `get_field_definitions`

Given a list of field keys, returns a corresponding list of field definitions.

Field definitions are used in user interfaces in order to provide differentiated and formatted display of sample field values. For instance, numbers may be formatted with thousands separators or a given number of significant digits. A field with a 'url' format may be displayed as a link. An ontology term can be correctly linked to the ontology landing page.

### Params:

- `keys` - `Array<string>` - an array of controlled field keys

### Result:

- `fields` - Array<SchemaField> - an array of field definitions.

### Where:

SchameField is

```typescript
import {JSONValue} from "@kbase/ui-lib/lib/json";

export type JSONSchemaFieldType =
    'string' |
    'number' |
    'boolean' |
    'object' |
    'array';

export interface JSONSchema {
    $schema: string;
    $id?: string;
    type: JSONSchemaFieldType
    format?: string
    title: string
    description?: string
    examples: Array<JSONValue>
}

export type ControlledFieldType =
    'string' |
    'number' |
    'boolean';

export interface ControlledFieldBase extends JSONSchema {
    type: ControlledFieldType;
    kbase: {
        format: {};
        unit: string,
        sample: {
            key: string
        }
    }
}

export interface ControlledFieldString extends ControlledFieldBase {
    type: 'string'
    minLength?: number
    maxLength?: number
    enum?: Array<string>;
    pattern?: string;
}

export interface ControlledFieldOntologyTerm extends ControlledFieldBase {
    type: 'string'
    format: 'ontologyTerm'
    ancestorTerm: string
    namespace: string
}

export interface ControlledFieldNumber extends ControlledFieldBase {
    type: 'number'
    minimum?: number
    minimumInclusive?: number
    maximum?: number
    maximumInclusive?: number
    kbase: ControlledFieldBase['kbase'] & {
        format: {
            useGrouping?: boolean;
            minimumFractionDigits?: number;
            maximumFractionDigits?: number;
            minimumSignificantDigits?: number;
            maximumSignificantDigits?: number;
            style?: "decimal" | "currency" | "percent" | "unit";
            notation?: "standard" | "scientific" | "engineering" | "compact";
        }
    };
}

export type ControlledField =
    ControlledFieldString |
    ControlledFieldOntologyTerm |
    ControlledFieldNumber;

```



