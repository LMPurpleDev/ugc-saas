import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { Controller, FormProvider, useFormContext } from "react-hook-form"

import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"

const Form = FormProvider

const FormField = ({ ...props }) => {
  return (
    <Controller
      {...props}
      render={({ field, fieldState, formState }) => {
        return (
          <FormItem>
            {React.cloneElement(props.children, {
              field,
              fieldState,
              formState,
            })}
          </FormItem>
        )
      }}
    />
  )
}

const FormItem = React.forwardRef(({
  className,
  ...props
}, ref) => {
  const { error, formItemId, formDescriptionId, formMessageId } = useFormContext()

  return (
    <div
      ref={ref}
      className={cn("space-y-2", className)}
      id={formItemId}
      aria-describedby={
        !error
          ? `${formDescriptionId}`
          : `${formDescriptionId} ${formMessageId}`
      }
      aria-invalid={!!error}
      {...props}
    />
  )
})
FormItem.displayName = "FormItem"

const FormLabel = React.forwardRef(({
  className,
  ...props
}, ref) => {
  const { formItemId } = useFormContext()

  return (
    <Label
      ref={ref}
      className={cn(className)}
      htmlFor={formItemId}
      {...props}
    />
  )
})
FormLabel.displayName = "FormLabel"

const FormControl = React.forwardRef(({
  ...props
}, ref) => {
  const { formItemId } = useFormContext()

  return (
    <Slot
      ref={ref}
      id={formItemId}
      {...props}
    />
  )
})
FormControl.displayName = "FormControl"

const FormDescription = React.forwardRef(({
  className,
  ...props
}, ref) => {
  const { formDescriptionId } = useFormContext()

  return (
    <p
      ref={ref}
      id={formDescriptionId}
      className={cn("text-[0.8rem] text-muted-foreground", className)}
      {...props}
    />
  )
})
FormDescription.displayName = "FormDescription"

const FormMessage = React.forwardRef(({
  className,
  children,
  ...props
}, ref) => {
  const { error, formMessageId } = useFormContext()
  const body = error ? String(error?.message) : children

  if (!body) {
    return null
  }

  return (
    <p
      ref={ref}
      id={formMessageId}
      className={cn("text-[0.8rem] font-medium text-destructive", className)}
      {...props}
    >
      {body}
    </p>
  )
})
FormMessage.displayName = "FormMessage"

export {
  useFormContext,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
}


