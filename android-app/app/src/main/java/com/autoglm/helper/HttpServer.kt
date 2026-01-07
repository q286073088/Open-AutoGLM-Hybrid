package com.autoglm.helper

import android.util.Log
import fi.iki.elonen.NanoHTTPD
import org.json.JSONObject
import java.io.ByteArrayInputStream

class HttpServer(private val service: AutoGLMAccessibilityService, port: Int = 8080) : NanoHTTPD("0.0.0.0", port) {

    companion object {
        private const val TAG = "AutoGLM-HttpServer"
    }

    init {
        // NanoHTTPD 2.3.1 没有直接的配置选项来禁用 Keep-Alive
        // 我们需要在每个响应中手动设置 Connection: close
        Log.i(TAG, "HttpServer initialized on port $port")
    }

    override fun serve(session: IHTTPSession): Response {
        val uri = session.uri
        val method = session.method

        Log.i(TAG, "Received request: $method $uri from ${session.headers["http-client-ip"] ?: "unknown"}")

        return try {
            val response = when {
                uri == "/status" && method == Method.GET -> handleStatus()
                uri == "/screenshot" && method == Method.GET -> handleScreenshot()
                uri == "/tap" && method == Method.POST -> handleTap(session)
                uri == "/swipe" && method == Method.POST -> handleSwipe(session)
                uri == "/input" && method == Method.POST -> handleInput(session)
                else -> createResponse(
                    Response.Status.NOT_FOUND,
                    "application/json",
                    """{"error": "Not found"}"""
                )
            }
            Log.i(TAG, "Response sent: $method $uri")
            response
        } catch (e: Exception) {
            Log.e(TAG, "Error handling request: $method $uri", e)
            createResponse(
                Response.Status.INTERNAL_ERROR,
                "application/json",
                """{"error": "${e.message}"}"""
            )
        }
    }

    /**
     * 创建响应并强制关闭连接
     * NanoHTTPD 2.3.1 的 Connection: close 处理有问题，需要手动关闭
     */
    private fun createResponse(status: Response.Status, mimeType: String, message: String): Response {
        val response = newFixedLengthResponse(status, mimeType, message)
        // 关键：必须在创建响应时就设置 Connection: close
        response.addHeader("Connection", "close")
        // 强制设置为 HTTP/1.0，避免持久连接
        response.addHeader("Server", "AutoGLM-Helper/1.0")
        return response
    }

    private fun handleStatus(): Response {
        val json = JSONObject()
        json.put("status", "ok")
        json.put("service", "AutoGLM Helper")
        json.put("version", "1.0.2")  // 更新版本号
        json.put("build", "20260107-nanohttpd-fix")  // 构建标识
        json.put("accessibility_enabled", service.isAccessibilityEnabled())

        return createResponse(
            Response.Status.OK,
            "application/json",
            json.toString()
        )
    }

    private fun handleScreenshot(): Response {
        val screenshot = service.takeScreenshotBase64()

        return if (screenshot != null) {
            val json = JSONObject()
            json.put("success", true)
            json.put("image", screenshot)
            json.put("format", "base64")

            createResponse(
                Response.Status.OK,
                "application/json",
                json.toString()
            )
        } else {
            val json = JSONObject()
            json.put("success", false)
            json.put("error", "Failed to take screenshot")

            createResponse(
                Response.Status.INTERNAL_ERROR,
                "application/json",
                json.toString()
            )
        }
    }

    private fun handleTap(session: IHTTPSession): Response {
        val body = getRequestBody(session)
        val json = JSONObject(body)

        val x = json.getInt("x")
        val y = json.getInt("y")

        val success = service.performTap(x, y)

        val response = JSONObject()
        response.put("success", success)

        return createResponse(
            Response.Status.OK,
            "application/json",
            response.toString()
        )
    }

    private fun handleSwipe(session: IHTTPSession): Response {
        val body = getRequestBody(session)
        val json = JSONObject(body)

        val x1 = json.getInt("x1")
        val y1 = json.getInt("y1")
        val x2 = json.getInt("x2")
        val y2 = json.getInt("y2")
        val duration = json.optInt("duration", 300)

        val success = service.performSwipe(x1, y1, x2, y2, duration)

        val response = JSONObject()
        response.put("success", success)

        return createResponse(
            Response.Status.OK,
            "application/json",
            response.toString()
        )
    }

    private fun handleInput(session: IHTTPSession): Response {
        val body = getRequestBody(session)
        val json = JSONObject(body)

        val text = json.getString("text")

        val success = service.performInput(text)

        val response = JSONObject()
        response.put("success", success)

        return createResponse(
            Response.Status.OK,
            "application/json",
            response.toString()
        )
    }

    private fun getRequestBody(session: IHTTPSession): String {
        val map = HashMap<String, String>()
        session.parseBody(map)
        return map["postData"] ?: ""
    }
}
