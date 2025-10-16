import { useEffect, useRef, useState } from 'react';

/**
 * Progressive left-to-right reveal effect.
 * Splits the text into characters (keeps newlines) and reveals them at a steady cadence.
 * Stops automatically when full text displayed or component unmounted.
 */
export default function useWordReveal(fullText: string, cps: number = 40) {
	const [displayed, setDisplayed] = useState('');
	const indexRef = useRef(0);
	const textRef = useRef(fullText);
	const timerRef = useRef<number | null>(null);

	useEffect(() => {
		// Reset when text changes
		textRef.current = fullText || '';
		indexRef.current = 0;
		setDisplayed('');

		if (!fullText) return;

		const step = () => {
			const target = textRef.current;
			if (indexRef.current >= target.length) {
				if (timerRef.current) cancelAnimationFrame(timerRef.current);
				return;
			}
			// reveal chunk proportional to frame time
			const nextIndex = Math.min(target.length, indexRef.current + Math.max(1, Math.round(cps / 10)));
			setDisplayed(target.slice(0, nextIndex));
			indexRef.current = nextIndex;
			timerRef.current = requestAnimationFrame(step);
		};
		timerRef.current = requestAnimationFrame(step);
		return () => {
			if (timerRef.current) cancelAnimationFrame(timerRef.current);
		};
	}, [fullText, cps]);

	return displayed;
}
