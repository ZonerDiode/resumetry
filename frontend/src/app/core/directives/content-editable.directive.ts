import {
  Directive,
  ElementRef,
  forwardRef,
  HostListener,
  inject,
  Renderer2,
  SecurityContext
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { DomSanitizer } from '@angular/platform-browser';

@Directive({
  selector: '[appContentEditable]',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => ContentEditableDirective),
      multi: true
    }
  ]
})
export class ContentEditableDirective implements ControlValueAccessor {
  private readonly el = inject(ElementRef<HTMLElement>);
  private readonly renderer = inject(Renderer2);
  private readonly sanitizer = inject(DomSanitizer);

  private onChange: (value: string) => void = () => {};
  private onTouched: () => void = () => {};

  @HostListener('input')
  onInput(): void {
    const html = this.el.nativeElement.innerHTML;
    const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, html) ?? '';
    this.onChange(sanitized);
  }

  @HostListener('blur')
  onBlur(): void {
    this.onTouched();
  }

  @HostListener('paste', ['$event'])
  onPaste(event: ClipboardEvent): void {
    event.preventDefault();

    const clipboardData = event.clipboardData;
    if (!clipboardData) return;

    let content = clipboardData.getData('text/html');
    if (!content) {
      content = clipboardData.getData('text/plain');
      content = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
    }

    const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, content) ?? '';
    document.execCommand('insertHTML', false, sanitized);
    this.onChange(this.el.nativeElement.innerHTML);
  }

  writeValue(value: string): void {
    const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, value ?? '') ?? '';
    this.renderer.setProperty(this.el.nativeElement, 'innerHTML', sanitized);
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.renderer.setAttribute(
      this.el.nativeElement,
      'contenteditable',
      isDisabled ? 'false' : 'true'
    );
  }
}
