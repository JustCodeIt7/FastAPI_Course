# Pydantic: A Comprehensive Guide

## What is Pydantic?

- **Definition:**
  - Pydantic extends Python's dataclasses with additional features:
    - **Validation:** Ensures data meets specified criteria.
    - **Serialization:** Converts data into formats suitable for other applications.
    - **Data Transformation:** Alters data shapes as needed.

- **Use Cases:**
  - Validating incoming data.
  - Transforming data structures.
  - Preparing data for serialization and transmission.

---

## A Really Basic Example

- **Objective:**
  - Ensure a function receives both `first_name` and `last_name` as strings.

- **Code Example:**
  ```python
  from pydantic import BaseModel

  class MyFirstModel(BaseModel):
      first_name: str
      last_name: str

  validating = MyFirstModel(first_name="marc", last_name="nealer")
  ```

- **Key Points:**
  - Pydantic models resemble Python dataclasses.
  - Unlike dataclasses, Pydantic enforces type validation and raises errors for mismatches.
  - **Default Validation:** Type checking is performed automatically.

---

## Handling Optional Parameters

- **Challenge:**
  - Managing optional fields with expected typing behaviors.

- **Code Example:**
  ```python
  from pydantic import BaseModel
  from typing import Union, Optional

  class MySecondModel(BaseModel):
      first_name: str
      middle_name: Union[str, None]  # Parameter is optional
      title: Optional[str]           # Parameter must be sent but can be None
      last_name: str
  ```

- **Explanation:**
  - **`Union[str, None]`:** Field is optional; it can be omitted.
  - **`Optional[str]`:** Field is required but can be `None`.
  - Pydantic leverages Python's `typing` library for comprehensive type validations.

- **Advanced Types Example:**
  ```python
  from pydantic import BaseModel
  from typing import Union, List, Dict
  from datetime import datetime

  class MyThirdModel(BaseModel):
      name: Dict[str, str]
      skills: List[str]
      holidays: List[Union[str, datetime]]
  ```

---

## Applying Default Values

- **Scenario:**
  - Assign default values to fields when data is missing.

- **Initial Approach:**
  ```python
  from pydantic import BaseModel

  class DefaultsModel(BaseModel):
      first_name: str = "jane"
      middle_names: list = []
      last_name: str = "doe"
  ```

- **Issue:**
  - Mutable default values (like lists) are shared across all instances, leading to unintended side effects.

- **Solution: Use `Field` with `default_factory`:**
  ```python
  from pydantic import BaseModel, Field

  class DefaultsModel(BaseModel):
      first_name: str = "jane"
      middle_names: list = Field(default_factory=list)
      last_name: str = "doe"
  ```

- **Benefits:**
  - Ensures each instance gets its own separate list.
  - Prevents shared mutable defaults.

- **Note on `Field`:**
  - Versatile but can complicate models if overused.
  - Recommended primarily for defaults and default factories.

---

## Nesting Models

- **Purpose:**
  - Organize complex data structures by embedding models within models.

- **Code Example:**
  ```python
  from pydantic import BaseModel

  class NameModel(BaseModel):
      first_name: str
      last_name: str

  class UserModel(BaseModel):
      username: str
      name: NameModel
  ```

- **Advantages:**
  - Promotes modularity and reusability.
  - Simplifies validation of nested data structures.

---

## Custom Validation

- **Need for Custom Validation:**
  - Beyond basic type checks, additional constraints are often required.

- **Types of Custom Validators:**
  - **Before Validators:** Modify or validate data before default validation.
  - **After Validators:** Perform checks after default validation.
  - **Wrap Validators:** Act like middleware, handling actions before and after.

- **Default Validation Context:**
  - **Field-Level:** Validates individual fields.
  - **Model-Level:** Validates the entire model, allowing inter-field dependencies.

### Field Validation

- **Approach:**
  - Utilize decorators to define validation functions for specific fields.
  - Prefer `Annotated` validators for clarity and maintainability.

- **Code Example:**
  ```python
  from pydantic import BaseModel, BeforeValidator, ValidationError
  from typing import Annotated
  import datetime

  def stamp2date(value):
      if not isinstance(value, float):
          raise ValidationError("Incoming date must be a timestamp")
      try:
          res = datetime.datetime.fromtimestamp(value)
      except ValueError:
          raise ValidationError("Timestamp appears to be invalid")
      return res

  class DateModel(BaseModel):
      dob: Annotated[datetime.datetime, BeforeValidator(stamp2date)]
  ```

- **Explanation:**
  - **`BeforeValidator`:** Transforms a timestamp (float) into a `datetime` object before default validation.
  - Ensures that the `dob` field receives a valid `datetime` object.

- **Multiple Validators Example:**
  ```python
  from pydantic import BaseModel, BeforeValidator, AfterValidator, ValidationError
  from typing import Annotated
  import datetime

  def one_year(value):
      if value < datetime.datetime.today() - datetime.timedelta(days=365):
          raise ValidationError("The date must be less than a year old")
      return value

  def stamp2date(value):
      if not isinstance(value, float):
          raise ValidationError("Incoming date must be a timestamp")
      try:
          res = datetime.datetime.fromtimestamp(value)
      except ValueError:
          raise ValidationError("Timestamp appears to be invalid")
      return res

  class DateModel(BaseModel):
      dob: Annotated[datetime.datetime, BeforeValidator(stamp2date), AfterValidator(one_year)]
  ```

- **Usage Insights:**
  - **`BeforeValidator`:** Ideal for data transformation and preliminary checks.
  - **`AfterValidator`:** Suitable for additional constraints post-transformation.
  - **`WrapValidator`:** Not extensively covered; author seeks community input on use cases.

- **Handling Optional Fields with Validators:**
  ```python
  from pydantic import BaseModel, BeforeValidator, ValidationError, Field
  from typing import Annotated
  import datetime

  def stamp2date(value):
      if not isinstance(value, float):
          raise ValidationError("Incoming date must be a timestamp")
      try:
          res = datetime.datetime.fromtimestamp(value)
      except ValueError:
          raise ValidationError("Timestamp appears to be invalid")
      return res

  class DateModel(BaseModel):
      dob: Annotated[Annotated[datetime.datetime, BeforeValidator(stamp2date)] | None, Field(default=None)]
  ```

- **Key Points:**
  - Combines `BeforeValidator` with `Optional` typing.
  - Allows `dob` to be omitted or set to `None`, while still enabling transformation when provided.

### Model Validation

- **Scenario:**
  - Ensuring at least one out of multiple optional fields is provided.

- **Code Example:**
  ```python
  from pydantic import BaseModel, model_validator, ValidationError
  from typing import Union, Any

  class AllOptionalAfterModel(BaseModel):
      param1: Union[str, None] = None
      param2: Union[str, None] = None
      param3: Union[str, None] = None

      @model_validator(mode="after")
      def there_must_be_one(self):
          if not (self.param1 or self.param2 or self.param3):
              raise ValidationError("One parameter must be specified")
          return self

  class AllOptionalBeforeModel(BaseModel):
      param1: Union[str, None] = None
      param2: Union[str, None] = None
      param3: Union[str, None] = None

      @model_validator(mode="before")
      @classmethod
      def there_must_be_one(cls, data: Any):
          if not (data.get("param1") or data.get("param2") or data.get("param3")):
              raise ValidationError("One parameter must be specified")
          return data
  ```

- **Explanation:**
  - **After Validation (`AllOptionalAfterModel`):**
    - Decorated method runs after model initialization.
    - Accesses fields via `self`.
  - **Before Validation (`AllOptionalBeforeModel`):**
    - Decorated method runs before model initialization.
    - Accesses raw input data (typically a dictionary).
    - Must return the (possibly modified) data.

- **Important Notes:**
  - **Decorator Order:** `@model_validator(mode="before")` must precede `@classmethod`.
  - **Error Handling:** Properly structured decorators prevent unexpected errors.
  - **Data Modification:** Before validators can alter input data before validation.

---

## Aliases in Pydantic

- **Purpose:**
  - Handle discrepancies between incoming data field names and model field names.
  - Facilitate data transformation during validation and serialization.

- **Types of Aliases:**
  - **Validation Aliases:** Incoming data has different field names than the model.
  - **Serialization Aliases:** Change field names when outputting serialized data.

- **Common Issue:**
  - Combining defaults with field-level aliases using `Field()` can be problematic.

- **Solution: Define Aliases at the Model Level:**
  ```python
  from pydantic import AliasGenerator, BaseModel, ConfigDict

  class Tree(BaseModel):
      model_config = ConfigDict(
          alias_generator=AliasGenerator(
              validation_alias=lambda field_name: field_name.upper(),
              serialization_alias=lambda field_name: field_name.title(),
          )
      )
      age: int
      height: float
      kind: str

  # Usage
  t = Tree.model_validate({'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'})
  print(t.model_dump(by_alias=True))  # Output: {'Age': 12, 'Height': 1.2, 'Kind': 'oak'}
  ```

- **Key Points:**
  - **Alias Generation:** Uses lambdas to transform field names during validation and serialization.
  - **Serialization Control:** `model_dump(by_alias=True)` ensures output uses serialization aliases.

### AliasChoices

- **Use Case:**
  - Handle multiple possible incoming field names for the same model field.

- **Code Example:**
  ```python
  from pydantic import BaseModel, ConfigDict, AliasGenerator, AliasChoices
  from typing import Union

  aliases = {
      "first_name": AliasChoices("fname", "surname", "forename", "first_name"),
      "last_name": AliasChoices("lname", "family_name", "last_name")
  }

  class FirstNameChoices(BaseModel):
      model_config = ConfigDict(
          alias_generator=AliasGenerator(
              validation_alias=lambda field_name: aliases.get(field_name, None)
          )
      )
      title: str
      first_name: str
      last_name: str
  ```

- **Explanation:**
  - **`AliasChoices`:** Specifies multiple possible names for a single field during validation.
  - **Inclusion of Actual Field Name:** Ensures compatibility when serializing and deserializing.

- **Practical Implications:**
  - Facilitates integration with diverse data sources where field naming conventions vary.
  - Simplifies data ingestion by accommodating various naming schemas.

### AliasPath

- **Use Case:**
  - Extract field values from nested dictionaries or lists within incoming data.

- **Code Example:**
  ```python
  from pydantic import BaseModel, ConfigDict, AliasGenerator, AliasPath

  aliases = {
      "first_name": AliasPath("name", "first_name"),
      "last_name": AliasPath("name", "last_name")
  }

  class FirstNameChoices(BaseModel):
      model_config = ConfigDict(
          alias_generator=AliasGenerator(
              validation_alias=lambda field_name: aliases.get(field_name, None)
          )
      )
      title: str
      first_name: str
      last_name: str

  # Usage
  obj = FirstNameChoices(**{
      "name": {"first_name": "marc", "last_name": "Nealer"},
      "title": "Master Of All"
  })
  ```

- **Explanation:**
  - **`AliasPath`:** Specifies the path to nested fields within the incoming data.
  - **Flattening Data:** Extracts `first_name` and `last_name` from the nested `name` dictionary, presenting them at the model's top level.

- **Benefits:**
  - Streamlines data models by abstracting nested structures.
  - Enhances readability and usability of models by flattening complex data.

### Combining AliasChoices and AliasPath

- **Objective:**
  - Leverage both `AliasChoices` and `AliasPath` for flexible and robust data handling.

- **Code Example:**
  ```python
  from pydantic import BaseModel, ConfigDict, AliasGenerator, AliasPath, AliasChoices

  aliases = {
      "first_name": AliasChoices("first_name", AliasPath("name", "first_name")),
      "last_name": AliasChoices("last_name", AliasPath("name", "last_name"))
  }

  class FirstNameChoices(BaseModel):
      model_config = ConfigDict(
          alias_generator=AliasGenerator(
              validation_alias=lambda field_name: aliases.get(field_name, None)
          )
      )
      title: str
      first_name: str
      last_name: str

  # Usage
  obj = FirstNameChoices(**{
      "name": {"first_name": "marc", "last_name": "Nealer"},
      "title": "Master Of All"
  })
  ```

- **Explanation:**
  - **Combined Aliases:** Allows `first_name` and `last_name` to be sourced either directly or from a nested `name` dictionary.
  - **Enhanced Flexibility:** Supports multiple data formats and sources seamlessly.

---

## Final Thoughts

- **Overall Impression:**
  - **Pydantic:** Highly powerful and versatile library.
  - **Complexity:** Offers multiple methods to achieve similar outcomes, which can be overwhelming initially.

- **Learning Curve:**
  - Understanding and effectively utilizing Pydantic requires substantial effort.
  - The guide aims to accelerate the learning process by providing clear examples and explanations.

- **Caution with AI Tools:**
  - AI services like ChatGPT and Gemini may provide inconsistent or incorrect information regarding Pydantic versions.
  - Recommendations:
    - Avoid relying on AI tools for Pydantic-specific coding.
    - Refer to official documentation and trusted resources instead.
