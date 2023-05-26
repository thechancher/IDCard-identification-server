const express = require("express")
const app = express()
const cors = require("cors")
app.use(cors({ origin: true }))

const functions = require("firebase-functions")

const serviceAccount = require("./key.json")
const admin = require("firebase-admin")
admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
})
const db = admin.firestore()

// main
app.get("/", (req, res) => {
    return res.status(200).send("Hello world!")
})

// POST: Register a person
app.post("/register", async (req, res) => {
    try {
        const { ID, DATE, CODE, NAME, LAST1, LAST2 } = req.body
        const data = { DATE, CODE, NAME, LAST1, LAST2 }

        const snapshot = await db.collection("padron").doc(ID).set(data)

        res.status(200).json({ status: "success", data: snapshot })
    } catch (error) {
        console.log(error)
        res.status(500).send({ status: "Failed. POST: Register a person", msg: error })
    }
})

// GET: personal data
app.get("/data", async (req, res) => {
    try {
        const key = req.query.key
        const access = await setLog(key)
        if (access) {
            const id = req.query.id
            const snapshot = db.collection("padron").doc(id)
            const userDetail = await snapshot.get()
            const response = userDetail.data()

            res.status(200).send({ status: "success", data: response })
        } else {
            res.status(200).send({ status: "access denied" })
        }
    } catch (error) {
        console.log(error)
        res.status(500).send({ status: "Failed. GET: personal data", msg: error })
    }
})


// POST: Retrieve the ID number
app.post("/id", async (req, res) => {
    try {
        const key = req.query.key
        const access = await setLog(key)
        if (access) {
            const { name, last1, last2 } = req.body

            const snapshot = await db.collection("padron")
                .where("NAME", "==", name)
                .where("LAST1", "==", last1)
                .where("LAST2", "==", last2)
                .get()

            const IDs = snapshot.docs.map(doc => doc.id)

            res.status(200).json({ status: "success", IDs })
        } else {
            res.status(200).send({ status: "access denied" })
        }
    } catch (error) {
        console.log(error)
        res.status(500).send({ status: "Failed. POST: Retrieve the ID number", msg: error })
    }
})

// GET: logger
app.get("/device", async (req, res) => {
    try {
        const id = req.query.id
        const snapshot = db.collection("device").doc(id)
        const deviceDetail = await snapshot.get()
        if (deviceDetail.exists) {
            const response = deviceDetail.data()
            res.status(200).send({ status: "success", data: response })
        } else {
            res.status(200).send({ status: "success", data: "device doesn't exist" })
        }
    } catch (error) {
        console.log(error)
        res.status(500).send({ status: "Failed. GET: device logs", msg: error })
    }
})

async function setLog(id) {
    try {
        const date = new Date()

        const snapshot = await db.collection("device").doc(id)
        const document = await snapshot.get();
        if (document.exists) {
            const updated = await snapshot.set({
                logs: admin.firestore.FieldValue.arrayUnion(date)
            }, { merge: true })

            if (updated.writeTime) {
                return true;
            } else {
                return false
            }
        } else {
            return false
        }

    } catch (error) {
        console.log(error)
        return false
    }
}

// POST: Set log
app.post("/log", async (req, res) => {
    try {
        const { key } = req.body

        const response = await setLog(key)
        console.log("response: ", response)

        res.status(200).json({ status: "success", data: response })

    } catch (error) {
        console.log(error)
        res.status(500).send({ status: "Failed. POST: Register a log", msg: error })
    }
})

// GET - count
app.get("/count", async (req, res) => {
    try {
        const registers = db.collection("padron")
        const snapshot = await registers.count().get()
        const count = snapshot.data().count

        return res.status(200).send({ status: "success", data: count })
    } catch (error) {
        console.log(error)
        res.status(500).send({ status: "Failed. count", msg: error })
    }
})

exports.app = functions.https.onRequest(app)