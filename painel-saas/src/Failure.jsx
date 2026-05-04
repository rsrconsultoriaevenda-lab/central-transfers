import React from 'react';
import { Link } from 'react-router-dom';

const Failure = () => {
    return (
        <div className="max-w-md mx-auto mt-20 p-8 bg-white rounded-xl shadow-2xl border-t-8 border-red-500">
            <div className="text-center mb-8">
                <div className="inline-block p-4 bg-red-100 rounded-full text-red-500 text-5xl mb-4">
                    ✕
                </div>
                <h1 className="text-3xl font-extrabold text-gray-900">Ops!</h1>
                <p className="text-gray-500 mt-2">Não conseguimos processar seu pagamento.</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6 text-center">
                <p className="text-gray-700 mb-4">
                    Isso pode ter acontecido por saldo insuficiente, dados incorretos ou expiração do tempo do PIX.
                </p>
                <p className="text-sm text-gray-500">
                    Sua reserva não foi confirmada. Por favor, tente novamente via WhatsApp.
                </p>
            </div>

            <div className="mt-10 flex flex-col gap-3">
                <a 
                    href="https://wa.me/SEU_NUMERO_DA_CENTRAL" 
                    className="bg-green-500 text-white py-3 px-6 rounded-lg font-bold text-center hover:bg-green-600 transition"
                >
                    Tentar novamente via WhatsApp
                </a>
                <Link to="/" className="text-gray-500 hover:text-gray-700 text-center text-sm font-medium">
                    Voltar ao início
                </Link>
            </div>
        </div>
    );
};

export default Failure;