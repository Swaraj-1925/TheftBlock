"use client"

import { useNavigate } from "react-router-dom"
import { Home } from "lucide-react"

function NotFound() {
    const navigate = useNavigate()

    return (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">404</h2>
            <p className="text-xl text-gray-600 mb-6">Page not found</p>
            <p className="text-gray-500 mb-8">The page you are looking for doesn't exist or has been moved.</p>
            <button
                onClick={() => navigate("/")}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
                <Home className="h-4 w-4 mr-2" />
                Back to Dashboard
            </button>
        </div>
    )
}

export default NotFound

