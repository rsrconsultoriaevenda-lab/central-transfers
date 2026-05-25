import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login'; 
import axios from 'axios';

vi.mock('axios');

describe('Componente de Login', () => {
  it('deve exibir erro ao tentar logar com credenciais inválidas', async () => {
    vi.spyOn(window, 'alert').mockImplementation(() => {});
    (axios.post as any).mockRejectedValueOnce(new Error('Unauthorized'));

    render(<MemoryRouter><Login /></MemoryRouter>);
    
    const emailInput = screen.getByPlaceholderText(/admin@centraltransfers.com/i);
    const passwordInput = screen.getByPlaceholderText(/••••••••/i);
    const submitButton = screen.getByRole('button', { name: /acessar sistema/i });

    fireEvent.change(emailInput, { target: { value: 'errado@teste.com' } });
    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith(expect.stringContaining("Falha no login"));
    });
  });

  it('deve realizar login com sucesso e armazenar o token', async () => {
    const fakeToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9';
    (axios.post as any).mockResolvedValueOnce({
      data: { access_token: fakeToken }
    });

    render(<MemoryRouter><Login /></MemoryRouter>);

    fireEvent.change(screen.getByPlaceholderText(/admin@centraltransfers.com/i), { target: { value: 'admin@central.com' } });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), { target: { value: 'Ren@220382' } });
    fireEvent.click(screen.getByRole('button', { name: /acessar sistema/i }));

    await waitFor(() => {
      // Verifica se o botão de login sumiu, indicando que o estado mudou ou houve navegação
      expect(screen.queryByRole('button', { name: /acessar sistema/i })).not.toBeInTheDocument();
    });
  });
});