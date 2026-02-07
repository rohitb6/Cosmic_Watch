/**
 * Live Solar System Visualization
 * 
 * Copyright © 2026 Rohit. Made with love by Rohit.
 * All rights reserved.
 * 
 * Real-time animated 3D solar system with planets orbiting the sun
 */
import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface Planet {
  name: string
  size: number
  distance: number
  speed: number
  color: string
  angle: number
}

export default function SolarSystem() {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const planetsRef = useRef<THREE.Mesh[]>([])
  const planetsDataRef = useRef<Planet[]>([
    { name: 'Mercury', size: 0.383, distance: 4, speed: 0.04, color: '#8c7853', angle: 0 },
    { name: 'Venus', size: 0.949, distance: 6, speed: 0.015, color: '#ffc649', angle: 0 },
    { name: 'Earth', size: 1, distance: 8, speed: 0.01, color: '#4a9eff', angle: 0 },
    { name: 'Mars', size: 0.532, distance: 10, speed: 0.008, color: '#ff6b6b', angle: 0 },
    { name: 'Jupiter', size: 11.21, distance: 14, speed: 0.002, color: '#c88b3a', angle: 0 },
    { name: 'Saturn', size: 9.45, distance: 18, speed: 0.0009, color: '#fad5a5', angle: 0 },
  ])

  useEffect(() => {
    if (!containerRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    sceneRef.current = scene
    scene.background = new THREE.Color(0x000814)
    scene.fog = new THREE.Fog(0x000814, 100, 500)

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      10000
    )
    camera.position.z = 35
    camera.position.y = 15

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.shadowMap.enabled = true
    containerRef.current.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Lighting
    const sunLight = new THREE.PointLight(0xfdb813, 2, 300)
    sunLight.position.set(0, 0, 0)
    sunLight.castShadow = true
    sunLight.shadow.mapSize.width = 2048
    sunLight.shadow.mapSize.height = 2048
    scene.add(sunLight)

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x333333)
    scene.add(ambientLight)

    // Create Sun
    const sunGeometry = new THREE.SphereGeometry(2, 32, 32)
    const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xfdb813 })
    const sun = new THREE.Mesh(sunGeometry, sunMaterial)
    sun.castShadow = true
    scene.add(sun)

    // Add glow to sun
    const glowGeometry = new THREE.SphereGeometry(2.3, 32, 32)
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0xfdb813,
      transparent: true,
      opacity: 0.15,
    })
    const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial)
    scene.add(glowMesh)

    // Create planets
    const planets: THREE.Mesh[] = []
    planetsDataRef.current.forEach((planetData) => {
      const geometry = new THREE.SphereGeometry(planetData.size, 32, 32)
      const material = new THREE.MeshStandardMaterial({
        color: planetData.color,
        roughness: 0.7,
        metalness: 0.3,
      })
      const planet = new THREE.Mesh(geometry, material)
      planet.castShadow = true
      planet.receiveShadow = true
      planet.userData = { ...planetData }
      planets.push(planet)
      scene.add(planet)
    })
    planetsRef.current = planets

    // Create orbit lines
    const orbits: THREE.Line[] = []
    planetsDataRef.current.forEach((planetData) => {
      const points: THREE.Vector3[] = []
      for (let i = 0; i <= 64; i++) {
        const angle = (i / 64) * Math.PI * 2
        points.push(
          new THREE.Vector3(Math.cos(angle) * planetData.distance, 0, Math.sin(angle) * planetData.distance)
        )
      }
      const curveGeometry = new THREE.BufferGeometry().setFromPoints(points)
      const curveMaterial = new THREE.LineBasicMaterial({ color: 0x444444, transparent: true, opacity: 0.3 })
      const curveObject = new THREE.Line(curveGeometry, curveMaterial)
      scene.add(curveObject)
      orbits.push(curveObject)
    })

    // Stars in background
    const starGeometry = new THREE.BufferGeometry()
    const starCount = 1000
    const starPositions = new Float32Array(starCount * 3)
    for (let i = 0; i < starCount * 3; i += 3) {
      starPositions[i] = (Math.random() - 0.5) * 400
      starPositions[i + 1] = (Math.random() - 0.5) * 400
      starPositions[i + 2] = (Math.random() - 0.5) * 400
    }
    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3))
    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.5,
      sizeAttenuation: true,
    })
    const stars = new THREE.Points(starGeometry, starMaterial)
    scene.add(stars)

    // Animation loop
    let animationId: number
    const animate = () => {
      animationId = requestAnimationFrame(animate)

      // Rotate planets
      planets.forEach((planet, index) => {
        const data = planetsDataRef.current[index]
        data.angle += data.speed

        planet.position.x = Math.cos(data.angle) * data.distance
        planet.position.z = Math.sin(data.angle) * data.distance

        // Rotate planets on their axis
        planet.rotation.y += 0.005

        // Add slight bobbing motion
        planet.position.y = Math.sin(data.angle * 0.5) * 0.2
      })

      // Rotate glowMesh
      glowMesh.rotation.z += 0.001

      // Rotate stars
      stars.rotation.x += 0.00001
      stars.rotation.y += 0.00001

      renderer.render(scene, camera)
    }
    animate()

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current || !renderer) return
      const width = containerRef.current.clientWidth
      const height = containerRef.current.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }
    window.addEventListener('resize', handleResize)

    // Mouse interaction - orbit camera
    let mouseX = 0
    let mouseY = 0
    const handleMouseMove = (event: MouseEvent) => {
      mouseX = (event.clientX / window.innerWidth) * 2 - 1
      mouseY = -(event.clientY / window.innerHeight) * 2 + 1
      camera.position.x = mouseX * 5
      camera.position.y = 15 + mouseY * 5
      camera.lookAt(0, 0, 0)
    }
    window.addEventListener('mousemove', handleMouseMove)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', handleMouseMove)
      cancelAnimationFrame(animationId)
      renderer.dispose()
      if (containerRef.current && renderer.domElement.parentNode === containerRef.current) {
        containerRef.current.removeChild(renderer.domElement)
      }
    }
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-2xl">🌌</div>
          <h2 className="text-xl font-bold text-cyan-400 font-heading">Live Solar System</h2>
        </div>
        <p className="text-xs text-gray-400">Move your mouse to rotate • Always updating</p>
      </div>
      <div
        ref={containerRef}
        className="w-full h-96 rounded-lg overflow-hidden border border-cyan-500/30 bg-gradient-to-b from-slate-950 to-blue-950/50"
      />
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2 text-center">
        {[
          { name: '☀️ Sun', color: 'text-yellow-400' },
          { name: '☿️ Mercury', color: 'text-gray-400' },
          { name: '♀️ Venus', color: 'text-yellow-300' },
          { name: '🌍 Earth', color: 'text-blue-400' },
          { name: '♂️ Mars', color: 'text-red-400' },
          { name: '♃ Jupiter', color: 'text-orange-600' },
          { name: '♄ Saturn', color: 'text-yellow-200' },
        ].map((planet) => (
          <div key={planet.name} className="text-xs">
            <div className={`font-semibold ${planet.color}`}>{planet.name}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
