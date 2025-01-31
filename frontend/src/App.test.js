import { render, screen } from '@testing-library/react';
import App from './App';

test('renders chomp chomp', () => {
  render(<App />);
  const linkElement = screen.getByText(/Chomp Chomp/);
  expect(linkElement).toBeInTheDocument();
});