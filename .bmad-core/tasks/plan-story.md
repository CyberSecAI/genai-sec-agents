# Plan Story Implementation

## ⚠️ CRITICAL EXECUTION NOTICE ⚠️

**THIS IS AN EXECUTABLE WORKFLOW - RUN BEFORE develop-story COMMAND**

When this task is invoked:

1. **MANDATORY PREREQUISITE**: A story file must exist in docs/stories/ before planning
2. **CREATE IMPLEMENTATION PLAN**: Generate detailed plan in docs/plans/ with same name
3. **USE STORY ANALYSIS**: Extract requirements from existing story for planning
4. **INTERACTIVE PLANNING**: Use plan-tmpl.yaml with user input for complex sections

## Purpose

Creates a detailed implementation plan for an existing user story to guide the development process. This plan should be created BEFORE running develop-story to ensure structured implementation.

## Input Requirements

- **Story ID**: The story identifier (e.g., "1.1.Project-Repository-Setup")
- **Story File**: Must exist at docs/stories/[STORY_ID].md
- **Output Location**: Plan will be created at docs/plans/[STORY_ID].md

## Execution Flow

### Step 1: Pre-Flight Checks
1. **Verify story exists** at docs/stories/[STORY_ID].md
2. **Check for existing plan** at docs/plans/[STORY_ID].md
3. **If plan exists**: Ask user to confirm overwrite (yes/no) - HALT if user says no

### Step 2: Story Analysis
1. **Load the story file** from docs/stories/[STORY_ID].md
2. **Extract key information**:
   - Story title and description
   - Acceptance criteria
   - Tasks and subtasks
   - Security requirements
   - Dev notes and architecture references

### Step 3: Plan Generation
1. **Use plan-tmpl.yaml** template with create-doc task
2. **Pre-populate context** from story analysis
3. **Interactive planning** for complex sections (marked elicit: true)
4. **Generate comprehensive plan** with:
   - Pre-implementation checklist
   - Detailed implementation steps with code examples
   - Verification procedures
   - Risk mitigation strategies

### Step 4: Plan Integration
1. **Save plan** to docs/plans/[STORY_ID].md
2. **Reference in story**: Add plan reference to Dev Notes if not present
3. **Validate completeness**: Ensure all story requirements are addressed in plan

## Command Usage

When user invokes plan-story, follow this pattern:

```
*plan-story [STORY_ID]
```

Example:
```
*plan-story 1.1.Project-Repository-Setup
```


## Validation Checklist

Before completing plan-story execution:

- [ ] Story file exists and was successfully loaded
- [ ] Existing plan check was performed and user confirmed overwrite if needed
- [ ] Plan addresses all acceptance criteria from story
- [ ] Implementation steps include specific commands/code where needed
- [ ] Security requirements are incorporated into planning
- [ ] Time estimates are realistic and detailed
- [ ] Risk mitigation covers identified technical challenges
- [ ] Plan file is saved with correct naming convention
- [ ] Plan references relevant architecture documents mentioned in story

## Integration with develop-story

After plan-story completion, the developer should:

1. **Review the plan** before starting implementation
2. **Use plan as implementation guide** during develop-story execution
3. **Update plan** if implementation reveals new requirements or issues
4. **Reference plan sections** when updating story completion notes

## Error Handling

If issues occur during planning:

- **Missing story file**: Halt and request user to provide valid story ID
- **Existing plan detected**: Ask user to confirm overwrite - HALT if user declines
- **Incomplete story**: Note missing elements and proceed with available information
- **Template issues**: Fall back to manual planning structure if template fails
- **File permissions**: Ensure write access to docs/plans/ directory

## Notes for Development Workflow

- This command should be run **BEFORE** develop-story
- Plans help ensure structured, thoughtful implementation
- Plans serve as documentation for complex implementation decisions
- Plans can be updated during implementation if requirements change